
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 크롤링할 법령명 리스트
law_names = [
    "공간정보의 구축 및 관리 등에 관한 법률",
    "공간정보의 구축 및 관리 등에 관한 법률 시행령",
    "공간정보의 구축 및 관리 등에 관한 법률 시행규칙",
    "국가공간정보 기본법",
    "국가공간정보 기본법 시행령",
    "공간정보산업 진흥법",
    "공간정보산업 진흥법 시행령",
    "공간정보산업 진흥법 시행규칙"
]

base_url = "https://www.law.go.kr"
search_url = "https://www.law.go.kr/lsSc.do?eventGubun=060101&query="

law_dict = {}

for law in law_names:
    encoded_query = urllib.parse.quote(law)
    url = search_url + encoded_query
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # '법령명'을 정확히 일치하는 a 태그 찾기
    law_link = soup.find("a", text=law)

    if law_link:
        href = law_link['href']
        # href 예시: "javascript:lawView('20341','');"
        if "lawView" in href:
            mst_id = href.split("'")[1]  # lawView('20341',''); 에서 20341 추출
            law_dict[law] = mst_id
            print(f"✅ {law} → mst_id: {mst_id}")
        else:
            print(f"❌ {law} → mst_id 추출 실패 (lawView 함수 없음)")
    else:
        print(f"❌ {law} → 검색 결과 없음")

print("\n🔍 최종 law_dict:")
print(law_dict)
