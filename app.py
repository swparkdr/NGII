import os
import difflib
import requests
from bs4 import BeautifulSoup
import streamlit as st

# =============== 공통 설정 =============== #
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

# =============== 법령 추적 함수 =============== #
def fetch_law_text(mst_id):
    url = f"https://www.law.go.kr/DRF/lawService.do?OC={API_KEY}&target=law&type=XML&mst={mst_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

def save_law_text(law_name, text):
    with open(f"{law_name}.txt", "w", encoding="utf-8") as f:
        f.write(text)

def load_law_text(law_name):
    if os.path.exists(f"{law_name}.txt"):
        with open(f"{law_name}.txt", "r", encoding="utf-8") as f:
            return f.read()
    return None

def compare_laws(old_text, new_text):
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))
    return diff

# =============== 행정규칙 추적 함수 =============== #
def crawl_rule_info(rule_name):
    url = "https://www.law.go.kr/admRulSc.do"
    params = {"query": rule_name}
    resp = requests.get(url, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")

    link = soup.select_one("a[href*='admRulLsInfoP.do']")
    if not link:
        return None

    detail_url = "https://www.law.go.kr" + link['href']
    detail = requests.get(detail_url)
    dsoup = BeautifulSoup(detail.text, "html.parser")

    title = dsoup.select_one(".law_view_title").get_text(strip=True)
    history = dsoup.select_one(".history_list li").get_text(strip=True)

    return {"name": title, "history": history, "url": detail_url}

def save_rule_history(rule_name, history):
    with open(f"{rule_name}_history.txt", "w", encoding="utf-8") as f:
        f.write(history)

def load_rule_history(rule_name):
    file_path = f"{rule_name}_history.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

# =============== Streamlit UI =============== #
st.set_page_config(page_title="NGII Law Keeper - 통합 시스템", layout="wide")
st.title("📚 NGII Law Keeper - 법령·행정규칙 통합 추적 시스템")

option = st.radio("🔎 추적할 항목을 선택하세요:", ("법령 추적", "행정규칙 추적"))

if option == "법령 추적":
    st.subheader("📜 법령 추적 시스템 (변경된 부분만 표시)")
    selected_law = st.selectbox("법령 선택", list(law_dict.keys()))

    if st.button("법령 추적 시작"):
        with st.spinner("법령을 추적하는 중입니다..."):
            mst_id = law_dict[selected_law]
            new_text = fetch_law_text(mst_id)

            if new_text:
                old_text = load_law_text(selected_law)

                if old_text:
                    diff = compare_laws(old_text, new_text)

                    if diff:
                        st.error(f"🚨 {selected_law}에 변경 사항이 있습니다!")
                        for line in diff:
                            if line.startswith('-'):
                                st.markdown(f"<span style='color:red;'>{line}</span>", unsafe_allow_html=True)
                            elif line.startswith('+'):
                                st.markdown(f"<span style='color:green;'>{line}</span>", unsafe_allow_html=True)
                        save_law_text(selected_law, new_text)
                    else:
                        st.info(f"✅ {selected_law}에 변경 사항이 없습니다. (표시 생략)")
                else:
                    st.warning("📂 이전 본문이 없습니다. 이번 본문을 기준으로 저장합니다.")
                    save_law_text(selected_law, new_text)
                    st.info("✅ 본문 저장 완료. 다음 추적부터 비교가 가능합니다.")
            else:
                st.error("❌ 법령 본문을 불러오지 못했습니다.")

elif option == "행정규칙 추적":
    st.subheader("📑 행정규칙 추적 시스템 (변경된 경우만 표시)")
    selected_rule = st.selectbox("행정규칙 선택", rule_list)

    if st.button("행정규칙 추적 시작"):
        with st.spinner("행정규칙을 검색하는 중입니다..."):
            result = crawl_rule_info(selected_rule)

            if result:
                old_history = load_rule_history(selected_rule)
                new_history = result["history"]

                if old_history:
                    if old_history != new_history:
                        st.error(f"🚨 {selected_rule}에 변경 사항이 있습니다!")
                        st.write(f"🔸 최신 연혁: {new_history}")
                        st.write(f"🔗 [바로가기]({result['url']})")
                        save_rule_history(selected_rule, new_history)
                    else:
                        st.info(f"✅ {selected_rule}에 변경 사항이 없습니다. (표시 생략)")
                else:
                    st.warning("📂 이전 이력이 없습니다. 이번 이력을 기준으로 저장합니다.")
                    save_rule_history(selected_rule, new_history)
                    st.info("✅ 이력 저장 완료. 다음 추적부터 비교가 가능합니다.")
            else:
                st.error("❌ 행정규칙을 불러오지 못했습니다.")
