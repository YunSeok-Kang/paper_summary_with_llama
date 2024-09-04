#!/bin/bash

# 주의 사항
# 1. 타겟 채널에 봇이 참여하고 있어야 함. 타겟 채널로 이동한 후, '/invite @봇이름'을 통해 봇을 채널에 참여시킬 수 있음
# 2. 해당 쉘 스크립트의 권한 확인 필요. chmod +x run_main.sh

# Conda 환경 이름
CONDA_ENV_NAME="paper_summary"

# 로그 파일 경로
LOG_FILE="execution_log.txt"

# 로그 파일에 기록 시작 시간 추가
echo "----- 실행 시작: $(date) -----" >> "$LOG_FILE"

# Conda 가상환경 활성화
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_NAME"

# 스크립트가 위치한 디렉토리로 이동
cd "$(dirname "$0")"

CHANNEL_NAME="논문요약테스트"

# SLACK_API_TOKEN은 환경 변수로 설정되어 있으므로 따로 명시하지 않음
# SLACK_API_TOKEN="$SLACK_API_TOKEN" 

# paper_url을 인자로 받아 처리
PAPER_URL="$1"

if [ -z "$PAPER_URL" ]; then
  echo "Error: paper_url이 제공되지 않았습니다." >> "$LOG_FILE"
  echo "Usage: $0 <paper_url>" >> "$LOG_FILE"
  exit 1
fi

# Python 스크립트 실행
python main_sh.py --target_channel_name "$CHANNEL_NAME" \
               --slack_api_token "$SLACK_API_TOKEN" \
               --paper_url "$PAPER_URL" >> "$LOG_FILE" 2>&1

# Conda 가상환경 비활성화
conda deactivate

# 로그 파일에 기록 종료 시간 추가
echo "----- 실행 종료: $(date) -----" >> "$LOG_FILE"
