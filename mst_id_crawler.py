import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

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

API_KEY = "lhs0623"
base_url = "https://www.law.go.kr"
search_url = "https://www.law.go.kr/lsSc.do?eventGubun=060101&query="
api_url = "https://www.law.go.kr/DRF/lawService.do"

law_dict = {}

for law in law_names:
    encoded_query = urllib.parse.quote(law)
    url = search_url + encoded_query
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        law_link = soup.find("a", text=law)

        if law_link:
            href = law_link['href']
            if "lawView" in href:
                mst_id = href.split("'")[1]

                # API 유효성 검사
                api_params = {"OC": API_KEY, "target": "law", "type": "XML", "mst": mst_id}
                api_response = requests.get(api_url, params=api_params)

                if "<Law>일치하는 법령이 없습니다." not in api_response.text:
                    law_dict[law] = mst_id
                    print(f"✅ {law} → 유효한 mst_id: {mst_id}")
                else:
                    print(f"❌ {law} → API에서 mst_id 불인정: {mst_id}")

                time.sleep(1)  # API 요청 딜레이 (서버 과부하 방지)
            else:
                print(f"❌ {law} → mst_id 추출 실패 (lawView 함수 없음)")
        else:
            print(f"❌ {law} → 검색 결과 없음")

    except Exception as e:
        print(f"❌ {law} → 크롤링 실패: {e}")

print("\n🔍 최종 유효 law_dict:")
print(law_dict)
