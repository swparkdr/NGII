import streamlit as st
import requests
import xml.etree.ElementTree as ET

# XML → Dictionary 변환 함수
def xml_to_dict(element):
    result = {}
    if len(element) == 0:
        return element.text
    for child in element:
        if child.tag not in result:
            result[child.tag] = xml_to_dict(child)
        else:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(xml_to_dict(child))
    return result

# API 호출 함수
def call_law_api(query="건축법"):
    url = "https://www.law.go.kr/LSO/openApi/searchLaw.do"
    params = {
        "OC": "네가 신청한 아이디",  # 여기 네 OC 입력
        "target": "law",
        "query": query,
        "display": 5,
        "page": 1,
        "type": "XML"
    }
    response = requests.get(url, params=params)
    tree = ET.fromstring(response.content)
    return xml_to_dict(tree)

# Streamlit UI
st.title("법제처 API 조회 (카드형 UI)")

query = st.text_input("검색어를 입력하세요", "건축법")

if st.button("검색"):
    with st.spinner("검색 중..."):
        result = call_law_api(query)

        try:
            items = result["LawSearch"]["law"]

            if not isinstance(items, list):
                items = [items]

            st.success(f"총 {len(items)}건 검색됨")

            for item in items:
                st.markdown("---")
                st.subheader(item.get("법령명한글", "법령명 없음"))
                st.write(f"공포일자: {item.get('공포일자', '정보 없음')}")
                st.write(f"소관부처: {item.get('소관부처명', '정보 없음')}")
                st.write(f"법령ID: {item.get('법령ID', '정보 없음')}")
                st.write(f"[법제처 바로가기](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq={item.get('법령ID', '')})")

        except Exception as e:
            st.error("결과를 불러오지 못했어요. 😢")
            st.write(e)
