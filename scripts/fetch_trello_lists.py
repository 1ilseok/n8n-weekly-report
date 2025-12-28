#!/usr/bin/env python3
"""
Trello 보드의 모든 List 정보를 조회하는 스크립트
"""
import requests
import json

# API 자격 증명
API_KEY = ""
API_TOKEN = ""
BOARD_ID = "rzSlarpY"

# API 엔드포인트
url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"

# 요청 파라미터
params = {
    "key": API_KEY,
    "token": API_TOKEN,
    "fields": "id,name,pos"
}

# API 호출
response = requests.get(url, params=params)

if response.status_code == 200:
    lists = response.json()
    print(f"총 {len(lists)}개의 List를 찾았습니다.\n")

    # List 정보 출력
    print("=" * 80)
    print(f"{'List 이름':<40} {'List ID':<30}")
    print("=" * 80)

    in_progress_list = None

    for lst in lists:
        list_name = lst['name']
        list_id = lst['id']
        print(f"{list_name:<40} {list_id:<30}")

        # "진행 중" List 찾기 (여러 가능한 이름 확인)
        if '진행' in list_name and '중' in list_name:
            in_progress_list = {
                'id': list_id,
                'name': list_name
            }

    print("=" * 80)

    # "진행 중" List 정보 저장
    if in_progress_list:
        print(f"\n✅ '진행 중' List를 찾았습니다:")
        print(f"   이름: {in_progress_list['name']}")
        print(f"   ID: {in_progress_list['id']}")

        # JSON 파일로 저장
        output_file = '/Users/ilseok/내 드라이브/n8n-weekly-report/scripts/trello_list_info.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'in_progress_list': in_progress_list,
                'all_lists': lists
            }, f, ensure_ascii=False, indent=2)

        print(f"\n📝 List 정보가 저장되었습니다: {output_file}")
    else:
        print("\n⚠️ '진행 중'이 포함된 List를 찾지 못했습니다.")
        print("   위의 List 목록에서 직접 선택해주세요.")

else:
    print(f"❌ API 호출 실패: {response.status_code}")
    print(response.text)
