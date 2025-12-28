#!/usr/bin/env python3
"""
카드 번호(#40)를 짧은 ID로 변환하는 스크립트
"""
import json

# 카드 매핑 데이터 로드
with open('/Users/ilseok/내 드라이브/n8n-weekly-report/scripts/trello_card_mapping.json', 'r', encoding='utf-8') as f:
    card_mapping = json.load(f)

# 카드 번호 -> 짧은 ID 매핑 딕셔너리 생성
number_to_shortlink = {}
for card_number, card_info in card_mapping.items():
    number_to_shortlink[f"#{card_number}"] = card_info['shortLink']

print("카드 번호 -> 짧은 ID 매핑:")
print(json.dumps(number_to_shortlink, ensure_ascii=False, indent=2))

# 변환 결과
conversions = {
    "#41": number_to_shortlink.get("#41", ""),
    "#9": number_to_shortlink.get("#9", ""),
    "#131": number_to_shortlink.get("#131", ""),
    "#14": number_to_shortlink.get("#14", ""),
    "#40": number_to_shortlink.get("#40", ""),
    "#121": number_to_shortlink.get("#121", ""),
    "#128": number_to_shortlink.get("#128", ""),
    "#119": number_to_shortlink.get("#119", ""),
    "#136": number_to_shortlink.get("#136", ""),
    "#114": number_to_shortlink.get("#114", ""),
    "#94": number_to_shortlink.get("#94", ""),
    "#74": number_to_shortlink.get("#74", "")
}

print("\n변환 결과:")
for card_num, short_id in conversions.items():
    print(f'{card_num} -> "{short_id}"')
