import json
import argparse
import yaml  # PyYAML 라이브러리 추가
from llm.llama import LlamaTextGenerator
from llm.llm_preprocess import build_llm_input
from utils.arxiv_loader import get_html_experimental_link, get_paper_abstract_content, get_paper_full_content, get_paper_title
from utils.md import create_markdown_file, sanitize_filename, SlackMessageFormatter
from slack_sdk import WebClient
import pytz
from datetime import datetime
import os

# 설정 파일 로드 함수 추가
def load_config(config_file="config.yaml"):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)

def send_msg_to_slack(text_msg, slack_api_token, slack_channel_name):
    sc = WebClient(token=slack_api_token)

    sc.chat_postMessage(
        channel=slack_channel_name,
        text=text_msg,
    )

def parse_multiple_json_objects(json_string):
    json_objects = []
    decoder = json.JSONDecoder()
    idx = 0

    while idx < len(json_string):
        obj, end_idx = decoder.raw_decode(json_string[idx:])
        json_objects.append(obj)
        idx += end_idx
        while idx < len(json_string) and json_string[idx] in " \n\t\r":
            idx += 1

    return json_objects

def save_summary_with_metadata(raw_summary, final_summary, paper_url, log_file_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_data = {
        "timestamp": timestamp,
        "paper_url": paper_url,
        "raw_summary": raw_summary,
        "final_summary": final_summary
    }
    
    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            try:
                data = json.load(log_file)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(summary_data)

    with open(log_file_path, "w", encoding="utf-8") as log_file:
        json.dump(data, log_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # 설정 파일 로드
    config = load_config()

    parser = argparse.ArgumentParser(description="Paper summary script.")
    parser.add_argument('--target_channel_name', type=str, required=False, default=config['slack']['channel_name'], help='Target Slack channel name.')
    parser.add_argument('--slack_api_token', type=str, required=False, default=config['slack']['api_token'], help='Slack API token.')
    parser.add_argument('--paper_url', type=str, required=True, help='URL of the paper to summarize.')
    
    args = parser.parse_args()

    paper_url = args.paper_url
    
    html_experimental_link = get_html_experimental_link(paper_url)
    if html_experimental_link == "Link not found":
        input_text = get_paper_abstract_content(paper_url)
    else:
        full_content = get_paper_full_content(html_experimental_link)
        input_text = build_llm_input(full_content)
        
    paper_title = get_paper_title(paper_url)
    
    model_id = config['paths']['model_id']
    text_generator = LlamaTextGenerator(model_id)
    
    summary = text_generator.generate_summary(input_text, temperature=0.5)
    
    kst = pytz.timezone('Asia/Seoul')
    current_time_kst = datetime.now(kst).strftime('%Y-%m-%d %H-%M-%S')
    
    slack_formatter = SlackMessageFormatter(summary)
    slack_message = slack_formatter.format_for_slack()
    
    slack_message = f"""*논문 제목: {paper_title}*
처리 시각: {current_time_kst}
url: {paper_url}
\n""" + slack_message
    
    save_summary_with_metadata(summary, summary, paper_url, config['paths']['log_file_path'])
    
    create_markdown_file(summary, sanitize_filename(paper_title), config['paths']['markdown_dir'])

    send_msg_to_slack(slack_message, args.slack_api_token, args.target_channel_name)
