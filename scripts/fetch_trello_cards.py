#!/usr/bin/env python3
"""
Trello 보드의 모든 카드 정보를 가져와서 카드 번호와 shortLink를 매핑합니다.
"""
import requests
import json

# Trello API 인증 정보
API_KEY = ""
API_TOKEN = ""
BOARD_ID = "rzSlarpY"

# API 엔드포인트
url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"

# 쿼리 파라미터
params = {
    "key": API_KEY,
    "token": API_TOKEN,
    "fields": "idShort,shortLink,name,id"
}

try:
    print("Trello API 호출 중...")
    response = requests.get(url, params=params)
    response.raise_for_status()

    cards = response.json()
    print(f"\n총 {len(cards)}개의 카드를 찾았습니다.\n")

    # 카드 정보를 idShort 순으로 정렬
    cards_sorted = sorted(cards, key=lambda x: x['idShort'])

    # 결과 출력
    print("=" * 80)
    print(f"{'카드 번호':<10} {'짧은 ID':<15} {'카드 이름'}")
    print("=" * 80)

    card_mapping = {}
    for card in cards_sorted:
        id_short = card['idShort']
        short_link = card['shortLink']
        name = card['name']

        print(f"#{id_short:<9} {short_link:<15} {name}")
        card_mapping[id_short] = {
            "shortLink": short_link,
            "name": name,
            "id": card['id']
        }

    print("=" * 80)

    # JSON 파일로 저장
    output_file = "/Users/ilseok/내 드라이브/n8n-weekly-report/scripts/trello_card_mapping.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(card_mapping, f, ensure_ascii=False, indent=2)

    print(f"\n결과가 {output_file}에 저장되었습니다.")

except requests.exceptions.RequestException as e:
    print(f"API 호출 실패: {e}")
    if hasattr(e.response, 'text'):
        print(f"응답: {e.response.text}")
except Exception as e:
    print(f"오류 발생: {e}")
