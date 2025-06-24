import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
import datetime

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

# 내부 규정 키워드 (샘플)
ngii_keywords = ["국가기준점", "측량", "공간정보", "무인비행장치"]

# 법령 본문 API
def fetch_law_text(mst_id):
    url = f"https://www.law.go.kr/DRF/lawService.do?OC={API_KEY}&target=law&type=XML&mst={mst_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
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

# 개정 요약 (간이 버전)
def summarize_law(text):
    soup = BeautifulSoup(text, "xml")
    articles = soup.find_all('조문내용')
    summary = []
    for article in articles[:3]:  # 처음 3개 조문만 요약
        content = article.get_text(strip=True)
        if content:
            summary.append(content[:100] + "...")
    return "\n".join(summary) if summary else "요약 불가"

# 내부 규정 영향 여부 판단
def check_internal_impact(summary):
    for keyword in ngii_keywords:
        if keyword in summary:
            return "Yes"
    return "No"

# 조치사항 추천
def recommend_action(impact, changed):
    if changed:
        if impact == "Yes":
            return "내부 지침 개정 필요, 담당자 알림 요망"
        else:
            return "담당자 알림 (참고용)"
    else:
        return "변경 사항 없음 (지속 모니터링)"

# 이메일 메시지 생성
def generate_email_message(law_name, date, summary, impact, action):
    return f"""📢 [국토지리정보 관련 법령 개정 알림 – {date}]

- 개정 법령: {law_name}
- 개정일: {date}
- 개정 요약: {summary}
- 내부규정 영향 여부: {impact}
- 조치사항: {action}
"""

st.set_page_config(page_title="NGII Law Keeper - 자동화 확장 버전", layout="wide")
st.title("📚 NGII Law Keeper - 법령 자동화 확장 버전")

option = st.radio("🔎 추적할 항목을 선택하세요:", ("법령 추적", "행정규칙 추적"))

if option == "법령 추적":
    st.subheader("📜 법령 추적 (자동 요약 + 영향 분석)")
    selected_law = st.selectbox("법령 선택", list(law_dict.keys()))

    if st.button("법령 추적 시작"):
        with st.spinner("법령을 추적하는 중입니다..."):
            mst_id = law_dict[selected_law]
            new_text = fetch_law_text(mst_id)

            if new_text:
                old_text = load_law_text(selected_law)
                today = datetime.datetime.today().strftime("%Y-%m-%d")

                changed = False
                if old_text:
                    if old_text != new_text:
                        changed = True
                        st.error(f"🚨 {selected_law}에 변경 사항이 있습니다!")
                        save_law_text(selected_law, new_text)
                    else:
                        st.info(f"✅ {selected_law}에 변경 사항이 없습니다.")
                else:
                    st.warning("📂 이전 본문이 없습니다. 이번 본문을 기준으로 저장합니다.")
                    save_law_text(selected_law, new_text)
                    st.info("✅ 본문 저장 완료. 다음 추적부터 비교가 가능합니다.")

                # ✅ 변경 여부와 상관없이 항상 요약, 분석, 이메일 생성
                summary = summarize_law(new_text)
                impact = check_internal_impact(summary)
                action = recommend_action(impact, changed)

                st.markdown("### 📋 법령 개정 요약")
                st.table({
                    "법령명": [selected_law],
                    "개정일": [today],
                    "주요 개정 내용": [summary],
                    "내부 규정 영향 여부": [impact],
                    "필요한 조치": [action]
                })

                email_message = generate_email_message(selected_law, today, summary, impact, action)
                st.markdown("### 📧 이메일용 메시지")
                st.code(email_message, language="text")

            else:
                st.error("❌ 법령 본문을 불러오지 못했습니다.")
