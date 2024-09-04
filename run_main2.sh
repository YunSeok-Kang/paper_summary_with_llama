#!/bin/bash

# Conda 환경 이름
CONDA_ENV_NAME="paper_summary"

# 로그 파일 경로와 채널 이름을 Python 스크립트를 통해 가져옴
CONFIG_FILE="config.yaml"
LOG_FILE=$(python -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['paths']['log_file'])")
CHANNEL_NAME=$(python -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['slack']['channel_name'])")

# 로그 파일에 기록 시작 시간 추가
echo "----- 실행 시작: $(date) -----" >> "$LOG_FILE"

# Conda 가상환경 활성화
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_NAME"

# 스크립트가 위치한 디렉토리로 이동
cd "$(dirname "$0")"

# paper_url을 인자로 받아 처리
PAPER_URL="$1"

if [ -z "$PAPER_URL" ]; then
  echo "Error: paper_url이 제공되지 않았습니다." >> "$LOG_FILE"
  echo "Usage: $0 <paper_url>" >> "$LOG_FILE"
  exit 1
fi

# Python 스크립트 실행
python main_sh.py --target_channel_name "$CHANNEL_NAME" \
               --paper_url "$PAPER_URL" >> "$LOG_FILE" 2>&1

# Conda 가상환경 비활성화
conda deactivate

# 로그 파일에 기록 종료 시간 추가
echo "----- 실행 종료: $(date) -----" >> "$LOG_FILE"
