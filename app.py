import requests
from bs4 import BeautifulSoup
import os

API_KEY = "lhs0623"
target_laws = [
    "공간정보의 구축 및 관리 등에 관한 법률",
    "공간정보의 구축 및 관리 등에 관한 법률 시행령",
    "공간정보의 구축 및 관리 등에 관한 법률 시행규칙",
    "국가공간정보 기본법",
    "국가공간정보 기본법 시행령",
    "공간정보산업 진흥법",
    "공간정보산업 진흥법 시행령",
    "공간정보산업 진흥법 시행규칙"
]

# 1. API에서 지원 법령 목록 가져오기
def fetch_law_list():
    url = f"https://www.law.go.kr/DRF/lawSearch.do?OC={API_KEY}&target=law&type=XML"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "xml")
    return soup.find_all("law")

# 2. 법령 본문 가져오기
def fetch_law_text(mst_id):
    url = f"https://www.law.go.kr/DRF/lawService.do?OC={API_KEY}&target=law&type=XML&mst={mst_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

# 3. 파일 저장 및 비교
def save_law_text(name, text):
    with open(f"{name}_law.txt", "w", encoding="utf-8") as f:
        f.write(text)

def load_law_text(name):
    file_path = f"{name}_law.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

# 4. 요약 (간단 비교용)
def summarize_law(text):
    soup = BeautifulSoup(text, "xml")
    try:
        law_name = soup.find("법령명").text.strip()
        law_date = soup.find("시행일자").text.strip()
        return law_name, law_date, "자동 요약 준비 중"
    except:
        return "Unknown", "Unknown", "요약 불가"

# 5. 메인 로직
def track_laws():
    law_list = fetch_law_list()
    tracked_laws = {law.find("법령명한글").text.strip(): law.find("법령일련번호").text.strip() for law in law_list if law.find("법령명한글").text.strip() in target_laws}

    for law_name, mst_id in tracked_laws.items():
        print(f"\n📋 {law_name} 추적 중...")
        new_text = fetch_law_text(mst_id)

        if new_text:
            old_text = load_law_text(law_name)

            if old_text:
                if old_text != new_text:
                    print(f"🚨 {law_name} 변경 사항 발견!")
                    law_name, law_date, summary = summarize_law(new_text)
                    print(f"📅 개정일: {law_date}")
                    print(f"📝 요약: {summary}")
                    save_law_text(law_name, new_text)
                else:
                    print(f"✅ {law_name} 변경 사항 없음.")
            else:
                print(f"📂 {law_name} 첫 저장.")
                save_law_text(law_name, new_text)
        else:
            print(f"❌ {law_name} 본문 불러오기 실패.")

track_laws()
