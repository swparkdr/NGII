import os
import requests
from bs4 import BeautifulSoup
import streamlit as st

API_KEY = "lhs0623"

law_dict = {
    "공간정보의 구축 및 관리 등에 관한 법률": "20341",
    "공간정보의 구축 및 관리 등에 관한 법률 시행령": "35246",
    "공간정보의 구축 및 관리 등에 관한 법률 시행규칙": "01387",
    "국가공간정보 기본법": "154971",
    "국가공간정보 기본법 시행령": "35246",
    "공간정보산업 진흥법": "17453",
    "공간정보산업 진흥법 시행령": "32541",
    "공간정보산업 진흥법 시행규칙": "00210"
}

rule_list = [
    "국토지리정보원 기본운영규정",
    "국토지리정보원 공간정보 표준화지침",
    "국가기준점 관리규정",
    "무인비행장치 측량 작업규정",
    "3차원국토공간정보구축작업규정"
]

# 행정규칙 크롤링 (User-Agent 적용)
def crawl_rule_info(rule_name):
    url = "https://www.law.go.kr/admRulSc.do"
    params = {"query": rule_name}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    }
    resp = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    link = soup.select_one("a[href*='admRulLsInfoP.do']")
    if not link:
        return None

    detail_url = "https://www.law.go.kr" + link['href']
    detail = requests.get(detail_url, headers=headers)
    dsoup = BeautifulSoup(detail.text, "html.parser")

    title = dsoup.select_one(".law_view_title").get_text(strip=True)
    history = dsoup.select_one(".history_list li").get_text(strip=True)

    return {"name": title, "history": history}

# 법령 본문 API
def fetch_law_text(mst_id):
    url = f"https://www.law.go.kr/DRF/lawService.do?OC={API_KEY}&target=law&type=XML&mst={mst_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def save_history(name, history):
    with open(f"{name}_history.txt", "w", encoding="utf-8") as f:
        f.write(history)

def load_history(name):
    file_path = f"{name}_history.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def save_law_text(name, text):
    with open(f"{name}_law.txt", "w", encoding="utf-8") as f:
        f.write(text)

def load_law_text(name):
    file_path = f"{name}_law.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

st.set_page_config(page_title="NGII Law Keeper - User-Agent 버전", layout="wide")
st.title("\ud83d\udcda NGII Law Keeper - User-Agent 적용 최종 버전")

option = st.radio("\ud83d\udd0e 추적할 항목을 선택하세요:", ("법령 추적", "행정규칙 추적"))

if option == "법령 추적":
    st.subheader("\ud83d\udcdc 법령 추적 (변경 여부만 표시)")
    selected_law = st.selectbox("법령 선택", list(law_dict.keys()))

    if st.button("법령 추적 시작"):
        with st.spinner("법령을 추적하는 중입니다..."):
            mst_id = law_dict[selected_law]
            new_text = fetch_law_text(mst_id)

            if new_text:
                old_text = load_law_text(selected_law)

                if old_text:
                    if old_text != new_text:
                        st.error(f"\ud83d\udea8 {selected_law}에 변경 사항이 있습니다!")
                        save_law_text(selected_law, new_text)
                    else:
                        st.info(f"\u2705 {selected_law}에 변경 사항이 없습니다.")
                else:
                    st.warning("\ud83d\udcc2 이전 본문이 없습니다. 이번 본문을 기준으로 저장합니다.")
                    save_law_text(selected_law, new_text)
                    st.info("\u2705 본문 저장 완료. 다음 추적부터 비교가 가능합니다.")
            else:
                st.error("\u274c 법령 본문을 불러오지 못했습니다.")

elif option == "행정규칙 추적":
    st.subheader("\ud83d\udcc1 행정규칙 추적 (User-Agent 적용)")
    selected_rule = st.selectbox("행정규칙 선택", rule_list)

    if st.button("행정규칙 추적 시작"):
        with st.spinner("행정규칙을 검색하는 중입니다..."):
            result = crawl_rule_info(selected_rule)

            if result:
                old_history = load_history(selected_rule)
                new_history = result["history"]

                if old_history:
                    if old_history != new_history:
                        st.error(f"\ud83d\udea8 {selected_rule}에 변경 사항이 있습니다!")
                        save_history(selected_rule, new_history)
                    else:
                        st.info(f"\u2705 {selected_rule}에 변경 사항이 없습니다.")
                else:
                    st.warning("\ud83d\udcc2 이전 이력이 없습니다. 이번 이력을 기준으로 저장합니다.")
                    save_history(selected_rule, new_history)
                    st.info("\u2705 이력 저장 완료. 다음 추적부터 비교가 가능합니다.")
            else:
                st.error("\u274c 행정규칙을 불러오지 못했습니다.")
