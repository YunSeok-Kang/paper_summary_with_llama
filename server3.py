import logging
from flask import Flask, request, jsonify, abort
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import re
import hmac
import hashlib
import time
import fcntl
import subprocess

# 현재는 rock 개념을 이용하여 여러 프로세스의 race condition을 제어함
# 그러나 봇이 요청을 받을 때, 이미 요청을 수행중인지 확인하고 그렇다면 그냥 무시하도록 하는 것이 좋을 것 같음

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(filename='slack_bot.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Slack Bot Token 및 Signing Secret
slack_token = os.environ.get("SLACK_BOT_TOKEN")
slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
client = WebClient(token=slack_token)

def verify_slack_request(data, timestamp, slack_signature):
    # 타임스탬프가 오래된 요청 거부 (5분 기준)
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    # 서명 데이터 생성
    sig_basestring = f"v0:{timestamp}:{data}".encode('utf-8')
    
    # HMAC-SHA256으로 서명 생성
    my_signature = 'v0=' + hmac.new(
        slack_signing_secret.encode('utf-8'),
        sig_basestring,
        hashlib.sha256
    ).hexdigest()
    
    # Slack 서명과 비교
    return hmac.compare_digest(my_signature, slack_signature)

processed_events = set()

@app.route('/slack/events', methods=['POST'])
def slack_events():
    slack_signature = request.headers.get('X-Slack-Signature')
    slack_request_timestamp = request.headers.get('X-Slack-Request-Timestamp')
    request_data = request.get_data(as_text=True)

    if not verify_slack_request(request_data, slack_request_timestamp, slack_signature):
        abort(400, "Invalid Slack request signature.")

    data = request.json

    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    if 'event' in data:
        event = data['event']

        event_id = data.get('event_id')
        if event_id in processed_events:
            # 이미 처리된 이벤트는 무시
            return jsonify({'status': 'ok'})

        processed_events.add(event_id)

        if event.get('type') == 'app_mention':
            user = event.get('user')
            text = event.get('text')
            channel = event.get('channel')

            logging.info(f"User: {user}, Channel: {channel}, Text: {text}")

            if "논문요약" in text:
                url = extract_url(text)

                if url:
                    if is_arxiv_url(url):
                        lock_file = "/tmp/gpu_task.lock"

                        with open(lock_file, 'w') as lock:
                            try:
                                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                                response_text = f"URL을 받았습니다: {url}. 처리를 시작합니다."
                                subprocess.run(["./run_main2.sh", url], shell=False)
                            except BlockingIOError:
                                response_text = "Another process is currently running the GPU task. Please try again later."
                            finally:
                                fcntl.flock(lock, fcntl.LOCK_UN)
                    else:
                        response_text = "현재 arXiv 논문만 입력할 수 있습니다. 올바른 arXiv URL을 입력해주세요."
                else:
                    response_text = "논문 URL을 찾을 수 없습니다. 올바른 URL을 입력해주세요."
            else:
                response_text = "명령어가 올바르지 않습니다. '논문요약' 키워드와 함께 URL을 입력해주세요."

            try:
                client.chat_postMessage(channel=channel, text=response_text)
            except SlackApiError as e:
                logging.error(f"Error sending message: {e.response['error']}")

    return jsonify({'status': 'ok'})

def extract_url(text):
    # 봇 ID를 제외하고 나머지 텍스트에서 URL 추출
    url_pattern = r'(https?://[^\s>]+)'
    match = re.search(url_pattern, text)
    
    if match:
        url = match.group(0)
        return url.strip('>')  # URL 끝에 있는 '>' 제거
    return None

def is_arxiv_url(url):
    # URL이 arXiv 출처인지 확인
    return url.startswith("https://arxiv.org/abs/")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
