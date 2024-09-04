import re
import os
from datetime import datetime

def create_markdown_file(text, filename, target_directory):
    # 타겟 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    # MarkdownGenerator 클래스 인스턴스 생성 및 파일 저장
    md_generator = MarkdownGenerator(text, filename, target_directory)
    saved_file_path = md_generator.save_markdown_file()

    print(f"Markdown 파일이 생성되었습니다: {saved_file_path}")
    return saved_file_path


def sanitize_filename(title):
    # 1. 소문자로 변환
    sanitized_title = title.lower()
    
    # 2. 특수 문자 제거 또는 대체
    # 일반적으로 파일명에서 사용하지 않는 문자: / \ : * ? " < > | 등을 제거
    sanitized_title = re.sub(r'[\/:*?"<>|]', '', sanitized_title)
    
    # 3. 공백 및 기타 문자 처리
    # 공백을 하이픈(-)으로 대체
    sanitized_title = re.sub(r'\s+', '-', sanitized_title)
    
    # 4. 이중 하이픈이나 언더바가 있을 경우 하나로 변환
    sanitized_title = re.sub(r'-+', '-', sanitized_title)

    # 5. 마지막으로 파일명에 쓸 수 있는 길이로 제한
    max_length = 255  # 일반적인 파일 시스템에서 파일명의 최대 길이
    sanitized_title = sanitized_title[:max_length].rstrip('-')
    
    return sanitized_title


class SlackMessageFormatter:
    def __init__(self, text):
        self.text = text

    def format_for_slack(self):
        # 제목을 굵게 변환
        formatted_text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', self.text)
        
        # 중복된 문구 제거 (원하는 경우)
        formatted_text = self.remove_duplicates(formatted_text)
        
        return formatted_text

    def remove_duplicates(self, text):
        sentences = text.split('\n')
        seen = set()
        result = []
        for sentence in sentences:
            if sentence not in seen:
                seen.add(sentence)
                result.append(sentence)
        return "\n".join(result)


# 클래스 정의는 이전에 설명한 그대로 사용
class MarkdownGenerator:
    def __init__(self, text, filename, target_directory):
        self.text = text
        self.filename = filename
        self.target_directory = target_directory

    def remove_duplicates(self, text):
        sentences = text.split('\n')
        seen = set()
        result = []
        for sentence in sentences:
            if sentence not in seen:
                seen.add(sentence)
                result.append(sentence)
        return "\n".join(result)

    def convert_to_markdown(self):
        # 중복된 문구 제거
        cleaned_text = self.remove_duplicates(self.text)
        # Markdown 제목 변환
        markdown_text = re.sub(r'\*\*(.*?)\*\*', r'# \1', cleaned_text)
        return markdown_text

    def save_markdown_file(self):
        # 현재 시각을 파일명에 추가
        timestamp = datetime.now().strftime("%H-%M-%S")
        complete_filename = f"{timestamp}_{self.filename}.md"
        file_path = os.path.join(self.target_directory, complete_filename)
        
        # Markdown 파일로 저장
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.convert_to_markdown())

        return file_path

if __name__ == "__main__":
    # 사용 예시
    text = """**Introduction**\n\nNeural Radiance Fields (NeRFs)가 처음 소개된 이후..."""  # 입력 텍스트
    filename = "ThermoNeRF_paper"  # 원하는 파일명 (확장자 제외)
    target_directory = "./markdown_files"  # 저장할 디렉토리 경로

    # 함수를 사용하여 Markdown 파일 생성
    saved_file_path = create_markdown_file(text, filename, target_directory)
