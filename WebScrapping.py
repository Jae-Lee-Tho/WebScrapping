import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json

# ChromeDriver 설정
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)

# 스크래핑할 페이지 리스트
url_list = [
    "https://mammothmemory.net/chemistry/periodic-table/elements-of-the-periodic-table/elements-of-the-periodic-table.html#chlorine"
]

def truncate_section_before_note(section_html: str, note_str: str = "NOTE:") -> str:
    note_index = section_html.find(note_str)
    if note_index != -1:
        return section_html[:note_index]
    return section_html

def get_raw_text(element) -> str:
    html = str(element)
    text_no_tags = re.sub(r"<.*?>", "", html, flags=re.DOTALL)
    text_clean = re.sub(r"\s+", " ", text_no_tags)
    return text_clean.strip()

def is_red_style(style_str: str) -> bool:
    style_str = style_str.lower().replace(" ", "")
    if "color:" in style_str:
        try:
            color_value = style_str.split("color:")[1].split(";")[0]
        except IndexError:
            return False
        if color_value in ["#ff0000", "red", "rgb(255,0,0)"]:
            return True
    return False

all_data = []

for url in url_list:
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    sections = soup.find_all("section", class_="content clearfix")
    
    for sec in sections:
        # "NOTE:" 이후 내용 제거
        section_html = str(sec)
        truncated_html = truncate_section_before_note(section_html, "NOTE:")
        sec_truncated = BeautifulSoup(truncated_html, 'html.parser')
        
        section_data = {}

        # 헤더(h1~h6) 추출
        h_tags = sec_truncated.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        for i, h in enumerate(h_tags, start=1):
            header_text = get_raw_text(h)
            if header_text:
                section_data[f"name{i}"] = header_text

        # 화학 페이지용 원소 이름/기호 검출 (원소 이름은 최종 결과에 포함하지 않음)
        element_name_tag = sec_truncated.find(id="pt-controls-name-mobile")
        element_symbol_tag = sec_truncated.find(id="pt-controls-symbol-mobile")
        element_name_text = ""
        symbol_text = ""
        if element_name_tag:
            element_name_text = get_raw_text(element_name_tag)
        if element_symbol_tag:
            symbol_text = get_raw_text(element_symbol_tag)
            if symbol_text:
                section_data["symbol_mobile"] = symbol_text

        # 문단(p) 추출 → 화학 기호 검출 시 첫 문단이 "원소이름 (기호)"면 건너뛰기
        p_tags = sec_truncated.find_all("p")
        p_count = 1
        for idx, p in enumerate(p_tags):
            paragraph_text = get_raw_text(p)
            if not paragraph_text:
                continue
            if element_name_text and symbol_text:
                expected_duplicate = f"{element_name_text} ({symbol_text})"
                if idx == 0 and paragraph_text == expected_duplicate:
                    continue
            section_data[f"p{p_count}"] = paragraph_text
            p_count += 1

        # 빨간색(highlight) 텍스트 추출
        red_elements = sec_truncated.find_all(lambda tag: tag.has_attr('style') and is_red_style(tag['style']))
        red_dict = {}
        for idx, red in enumerate(red_elements, start=1):
            red_text = get_raw_text(red)
            if red_text:
                red_dict[f"red{idx}"] = red_text
        if red_dict:
            section_data["red_content"] = red_dict

        # 이미지(img) 추출 (예시: 화학 페이지의 경우 두번째 이미지는 건너뛰도록 설정)
        img_tags = sec_truncated.find_all("img")
        included_img_count = 1
        for j, img in enumerate(img_tags, start=1):
            if "chemistry" in url.lower() and j == 2:
                continue
            src = img.get("src", "")
            if src:
                if not src.startswith("http"):
                    src = "https://mammothmemory.net" + src
                section_data[f"img{included_img_count}_src"] = src
                included_img_count += 1

        # === 여기서 figcaption 텍스트를 p2에 추가하는 부분만 추가 ===
        figcaptions = sec_truncated.find_all("figcaption")
        caption_texts = []
        for fc in figcaptions:
            fc_text = get_raw_text(fc)
            if fc_text:
                caption_texts.append(fc_text)

        if caption_texts:
            joined_caption = " ".join(caption_texts)
            # 만약 이미 p2가 있다면 뒤에 이어 붙이고, 없으면 p2 새로 생성
            if "p2" in section_data:
                section_data["p2"] = section_data["p2"] + " " + joined_caption
            else:
                section_data["p2"] = joined_caption
        # === 추가 끝 ===

        if section_data:
            all_data.append(section_data)

driver.quit()

# 결과 JSON 저장
with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)

print("크롤링 완료! result.json에 저장되었습니다.")