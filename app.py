import requests
from bs4 import BeautifulSoup
import os

API_KEY = "lhs0623"

# 추적할 법령 키워드 리스트
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

# 법령 목록 가져오기
def fetch_law_list():
    url = f"https://www.law.go.kr/DRF/lawSearch.do?OC={API_KEY}&target=law&type=XML"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "xml")
        return soup.find_all("law")
    else:
        print("❌ 법령 목록 불러오기 실패.")
        return []

# 본문 가져오기
def fetch_law_text(mst_id):
    url = f"https://www.law.go.kr/DRF/lawService.do?OC={API_KEY}&target=law&type=XML&mst={mst_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

# 파일 저장
def save_law_text(name, text):
    with open(f"{name}_law.txt", "w", encoding="utf-8") as f:
        f.write(text)

# 파일 불러오기
def load_law_text(name):
    file_path = f"{name}_law.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

# 간단 요약 (추후 고도화 가능)
def summarize_law(text):
    soup = BeautifulSoup(text, "xml")
    try:
        law_name = soup.find("법령명").text.strip()
        law_date = soup.find("시행일자").text.strip()
        return law_name, law_date, "요약 준비 중"
    except:
        return "Unknown", "Unknown", "요약 불가"

# 메인 추적기
def track_laws():
    print("\n📥 법령 목록 불러오는 중...")
    law_list = fetch_law_list()
    print(f"📄 총 {len(law_list)}건의 법령을 불러왔습니다.")

    tracked_laws = {}

    for law in law_list:
        law_name = law.find("법령명한글").text.strip()
        mst_id = law.find("법령일련번호").text.strip()

        if any(target in law_name for target in target_laws):
            tracked_laws[law_name] = mst_id

    print(f"🔎 추적할 법령 수: {len(tracked_laws)}")

    if len(tracked_laws) == 0:
        print("⚠️ 필터링된 법령이 없습니다. 키워드를 다시 확인하세요.")
        return

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
                print(f"📂 {law_name} 첫 저장 완료.")
                save_law_text(law_name, new_text)
        else:
            print(f"❌ {law_name} 본문 불러오기 실패.")

if __name__ == "__main__":
    track_laws()
