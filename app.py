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
    content_type = response.headers.get('Content-Type', '')

    # XML 응답이 아닐 때 방어
    if 'xml' not in content_type.lower():
        raise ValueError(f"XML이 아닌 응답이 왔어요: {content_type}\n응답 내용: {response.text[:300]}")

    # 빈 응답 방어
    if not response.content.strip():
        raise ValueError("응답이 비어있어요.")

    try:
        tree = ET.fromstring(response.content)
    except ET.ParseError as e:
        raise ValueError(f"XML 파싱 실패: {e}\n응답 내용: {response.text[:300]}")

    return xml_to_dict(tree)

# Streamlit UI
st.title("법제처 API 조회 (카드형 UI + 오류 방어)")

query = st.text_input("검색어를 입력하세요", "건축법")

if st.button("검색"):
    with st.spinner("검색 중..."):
        try:
            result = call_law_api(query)

            if "LawSearch" not in result:
                st.error("결과를 불러올 수 없습니다.")
            else:
                items = result["LawSearch"].get("law", [])

                if isinstance(items, dict):
                    items = [items]

                if len(items) == 0:
                    st.warning("검색 결과가 없습니다.")
                else:
                    st.success(f"총 {len(items)}건 검색됨")

                    for item in items:
                        st.markdown("---")
                        st.subheader(item.get("법령명한글", "법령명 없음"))
                        st.write(f"공포일자: {item.get('공포일자', '정보 없음')}")
                        st.write(f"소관부처: {item.get('소관부처명', '정보 없음')}")
                        st.write(f"법령ID: {item.get('법령ID', '정보 없음')}")
                        st.write(f"[법제처 바로가기](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq={item.get('법령ID', '')})")

        except Exception as e:
            st.error("API 호출 중 오류가 발생했어요. 😢")
            st.write(str(e))
