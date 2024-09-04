import random
import time

import requests
from bs4 import BeautifulSoup


def get_html_experimental_link(paper_url):
    response = requests.get(paper_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 'HTML (experimental)' 링크 찾기
    html_link = soup.find("a", string="HTML (experimental)")
    if html_link:
        return html_link["href"]  # 링크 추출
    else:
        return "Link not found"
    
    
def get_paper_abstract_content(paper_url):
    for trial in range(3):
        try:
            response = requests.get(paper_url)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}. Retrying in {trial * 30 + 15} seconds...")
            time.sleep(trial * 30 + 15)
    else:
        return "Failed to retrieve the paper after multiple attempts."

    # BeautifulSoup을 사용하여 HTML 내용을 파싱합니다.
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Abstract 부분을 추출합니다.
    abstract = soup.find('blockquote', class_='abstract')
    
    # 텍스트에서 'Abstract:' 부분을 제거하고 반환합니다.
    if abstract:
        abstract_text = abstract.get_text(strip=True).replace('Abstract:', '').strip()
        return abstract_text
    else:
        return "Abstract not found."
    
    
def get_paper_title(paper_url):
    for trial in range(3):
        try:
            response = requests.get(paper_url)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}. Retrying in {trial * 30 + 15} seconds...")
            time.sleep(trial * 30 + 15)
    else:
        return "Failed to retrieve the paper after multiple attempts."

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find('h1', class_='title')
    
    if title:
        title_text = title.get_text(strip=True).replace('Title:', '').strip()
        return title_text
    else:
        return "Title not found."
    
# def get_paper_abstract_content(paper_url):
#     for trial in range(3):
#         try:
#             paper_page = requests.get(paper_url)
#             if paper_page.status_code == 200:
#                 break
#         except requests.exceptions.ConnectionError as e:
#             print(e)
#             time.sleep(trial * 30 + 15)
            
#     response = paper_page
    
#     # BeautifulSoup을 사용하여 HTML 내용을 파싱합니다.
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     # Abstract 부분을 추출합니다.
#     abstract = soup.find('blockquote', class_='abstract')
    
#     # 텍스트에서 'Abstract:' 부분을 제거하고 반환합니다.
#     if abstract:
#         abstract_text = abstract.get_text(strip=True).replace('Abstract:', '').strip()
#         return abstract_text
#     else:
#         return "Abstract not found."
    
    
def get_paper_full_content(paper_url):
    for trial in range(3):
        try:
            paper_page = requests.get(paper_url)
            if paper_page.status_code == 200:
                break
        except requests.exceptions.ConnectionError as e:
            print(e)
            time.sleep(trial * 30 + 15)
    paper_soup = BeautifulSoup(paper_page.text, "html.parser")

    sections = paper_soup.find_all("section")
    section_dict = {}

    for section in sections:
        section_id = section.get("id")
        if section_id:
            # <h2> 태그 내에서 제목 찾기
            title_tag = section.find("h2")
            if title_tag:
                # <span> 태그 내용 제거
                if title_tag.find("span"):
                    title_tag.span.decompose()
                section_title = title_tag.text.strip()
            else:
                section_title = "No title found"

            # 섹션의 전체 텍스트 내용을 추출 (제목 제외)
            section_content = "\n".join(
                [para.text.strip() for para in section.find_all("p")]
            )

            # 사전에 섹션 ID, 제목, 내용 저장
            section_dict[section_id] = {
                "title": section_title,
                "content": section_content,
            }

    return section_dict