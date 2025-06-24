import requests
from bs4 import BeautifulSoup

# HTML 파일 불러오기
with open('/mnt/data/법령검색목록.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# 행정규칙ID 추출
rows = soup.find_all('tr', class_='gr')
law_ids = []

for row in rows:
    tds = row.find_all('td')
    if len(tds) >= 2:
        law_id = tds[1].text.strip()
        law_ids.append(law_id)

print(f"총 {len(law_ids)}건의 행정규칙ID를 추출했어!")

# 하나 테스트 호출
test_id = law_ids[0]
api_url = f"https://www.law.go.kr/LSO/openApi/viewAdmRul.do?OC=lhs0623&mst={test_id}&type=XML"

response = requests.get(api_url)
if response.status_code == 200:
    print("API 호출 성공!")
    print(response.text)  # 여기에 본문이 나올 거야
else:
    print("API 호출 실패..")
