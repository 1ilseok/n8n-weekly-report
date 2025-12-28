# 업무일지 Trello 자동화 구현 요약

## 📋 변경사항 개요

### 1. Trello 카드 ID 매핑 방식 변경

**기존 방식:**
```yaml
trello_card_mapping:
  Redmine: "여기에_카드ID_입력"
  자동화: "여기에_카드ID_입력"
  인프라: "여기에_카드ID_입력"
```

**새로운 방식:**
```yaml
trello_card_mapping:
  Privacy-i MacOS Agent 자동화: "VHYpqMEd"
  SQL Commit마다 스키마 생성/업데이트 비교 자동화: "Lv1j08Ng"
  somansa custom shell 개발: "mFQmAnZ7"
  기타 업무: "PepODzWV"
```

**변경 이유:**
- 카테고리 대신 구체적인 업무/프로젝트명 사용
- 긴 카드 ID 대신 짧은 ID (shortLink) 사용
- AI가 업무 내용을 분석하여 적절한 카드 자동 선택

---

## 🔧 Trello API 구조

### 카드 ID 형식
- **긴 ID**: `6005c293e776d56d07d8a362` (API 내부에서 사용)
- **짧은 ID (shortLink)**: `Lv1j08Ng` (URL에서 사용, 우리가 사용할 형식)
- **카드 번호**: `#40` (사용자가 보는 번호)

### Trello URL 구조
```
https://trello.com/c/VHYpqMEd/9-privacy-i-macos-agent-자동화
                      ^^^^^^^^
                      짧은 ID (shortLink)
```

### API 엔드포인트

#### 1. 짧은 ID로 카드 정보 조회
```
GET https://api.trello.com/1/cards/{shortLink}
Query Parameters:
  - key: {API_KEY}
  - token: {API_TOKEN}
  - fields: id,name,shortLink
```

#### 2. 카드에 댓글 추가
```
POST https://api.trello.com/1/cards/{cardId}/actions/comments
Query Parameters:
  - key: {API_KEY}
  - token: {API_TOKEN}
Body Parameters:
  - text: 댓글 내용
```

#### 3. 카드를 다른 List로 이동
```
PUT https://api.trello.com/1/cards/{cardId}
Query Parameters:
  - key: {API_KEY}
  - token: {API_TOKEN}
  - idList: {LIST_ID}
```

**사용 가능한 List:**
- 진행 중: `5fc8430caeb8b073ed11d2be`
- 대기 중: `5fc89f59596bd95a3f25e7c3`
- 진행 대기: `5fc9e151255ee313b2dab9c1`
- 진행 완료: `5fcecb7ed92b5b0794b9ea83`

---

## 🤖 n8n 워크플로우 v3 구조 (카테고리 기반)

### 노드 구성

1. **트리거**
   - 매일 18시 자동 실행
   - 수동 실행 (날짜 지정 가능)

2. **업무일지 읽기**
   - 지정된 날짜의 마크다운 파일 읽기
   - 파일 경로: `/Users/ilseok/내 드라이브/n8n-weekly-report/daily-worklogs/YYYY-MM/YYYY-MM-DD.md`

3. **업무일지 파싱 (카테고리 기반)** ⭐ 개선됨
   - YAML Front Matter에서 `trello_card_mapping` 추출
   - YAML Front Matter에서 `category` 추출
   - "업무 현황" 통합 테이블 파싱 (상태 무관 전체 파싱)
   - 각 업무의 카테고리에 해당하는 카드만 필터링하여 제공

4. **업무 항목 반복**
   - 각 업무를 순차적으로 처리

5. **AI 카드 선택 (카테고리 기반)** ⭐ 개선됨
   - OpenAI API를 사용하여 업무 내용 분석
   - 해당 카테고리의 카드 중에서만 선택
   - 가장 관련성 높은 Trello 카드 자동 선택
   - 선택 이유 함께 반환

6. **AI 응답 파싱**
   - AI 응답에서 JSON 추출
   - 선택된 카드의 짧은 ID 추출

7. **짧은ID로 긴ID 조회**
   - Trello API를 사용하여 짧은 ID로 긴 ID 조회
   - 긴 ID는 댓글 추가 API에 필요

8. **Trello 댓글 추가**
   - 선택된 카드에 업무 내용 댓글로 추가
   - 댓글 형식:
     ```
     📌 상태: {상태}
     📝 업무 내용: {업무 내용}
     📊 진도: {진도}
     ⚡ 우선순위: {우선순위} | 난이도: {난이도}
     ⏱️ 소요시간: {소요시간}
     📅 작업일: {작업일} | 예상 완료일: {예상 완료일}
     ```

9. **카드를 '진행 중'으로 이동** ⭐ 신규 추가
   - 댓글이 추가된 카드를 자동으로 "진행 중" List로 이동
   - 카드가 어느 List에 있든 상관없이 항상 "진행 중"으로 이동
   - List ID: `5fc8430caeb8b073ed11d2be`

10. **반복 완료 확인**
    - 모든 업무 처리 완료 확인

11. **동기화 상태 업데이트**
    - 파일의 `trello_synced: false`를 `true`로 변경
    - 중복 동기화 방지

---

## 📁 파일 구조

```
n8n-weekly-report/
├── daily-worklogs/
│   └── 2025-12/
│       └── 2025-12-27.md             # 업무일지 (짧은 ID로 업데이트됨)
├── templates/
│   └── daily-worklog-template-v2.md  # 템플릿 (category 필드 포함)
├── workflows/
│   ├── daily-to-trello.json          # v1: 기존 워크플로우
│   ├── daily-to-trello-v2.json       # v2: AI 기반 (전체 카드에서 선택)
│   └── daily-to-trello-v3.json       # v3: AI 기반 (카테고리 필터링) ⭐ 권장
├── scripts/
│   ├── fetch_trello_cards.py         # Trello 카드 정보 조회 스크립트
│   ├── fetch_trello_lists.py         # Trello List 정보 조회 스크립트
│   ├── convert_card_numbers.py       # 카드 번호 -> 짧은 ID 변환
│   ├── trello_card_mapping.json      # 카드 번호-ID 매핑 데이터
│   └── trello_list_info.json         # List 정보 (진행 중 List ID 포함)
└── docs/
    └── implementation-summary.md     # 이 문서
```

---

## 🚀 사용 방법

### 1. Trello 카드 정보 업데이트

```bash
cd "/Users/ilseok/내 드라이브/n8n-weekly-report"
python3 scripts/fetch_trello_cards.py
```

이 스크립트는:
- Trello API로 모든 카드 정보 조회
- 카드 번호, 짧은 ID, 카드명 매핑
- `scripts/trello_card_mapping.json`에 저장

### 2. 업무일지 작성

[daily-worklog-template-v2.md](../templates/daily-worklog-template-v2.md)를 참고하여 작성:

```yaml
---
date: 2025-12-27
day: 토요일
week_number: 52
author: 김일석
trello_card_mapping:
  Privacy-i MacOS Agent 자동화: "VHYpqMEd"
  SQL Commit마다 스키마 생성/업데이트 비교 자동화: "Lv1j08Ng"
  기타 업무: "PepODzWV"
total_hours: 0
trello_synced: false
---
```

### 3. n8n 워크플로우 설정

1. n8n에 [daily-to-trello-v3.json](../workflows/daily-to-trello-v3.json) 임포트 ⭐ 권장
   - v2: 전체 카드 목록에서 AI가 선택
   - v3: 카테고리별 카드만 AI에게 제공 (더 정확함)
2. OpenAI API 자격 증명 설정
3. Trello API 자격 증명 설정 (또는 하드코딩된 키/토큰 사용)
4. 워크플로우 활성화

### 4. 실행

- **자동 실행**: 매일 18시에 자동으로 실행
- **수동 실행**: n8n에서 수동 트리거 클릭, 날짜 입력 (YYYY-MM-DD)

---

## 🔑 API 자격 증명

### Trello API
- **API Key**: ``
- **API Token**: ``
- **Board ID**: `rzSlarpY`

### OpenAI API
- n8n에서 설정 필요
- 모델: GPT-4 또는 GPT-3.5-turbo 권장

---

## ⚠️ 주의사항

1. **API 키 보안**
   - 프로덕션 환경에서는 환경 변수 사용 권장
   - 현재는 테스트용으로 하드코딩됨

2. **AI 응답 처리**
   - AI가 JSON 형식을 잘못 반환할 경우 "기타 업무" 카드로 폴백
   - 파싱 에러 로그 확인 필요

3. **중복 동기화 방지**
   - `trello_synced: true`인 파일은 자동으로 건너뜀
   - 재동기화가 필요하면 수동으로 `false`로 변경

4. **파일 경로**
   - 절대 경로 사용: `/Users/ilseok/내 드라이브/n8n-weekly-report/...`
   - 환경에 따라 경로 수정 필요

---

## 📊 AI 선택 로직 (v3 카테고리 기반)

### 동작 방식

1. **카테고리 필터링**
   - 업무일지 테이블의 "카테고리" 컬럼 값 확인
   - `category` 필드에서 해당 카테고리의 카드 ID 리스트 조회
   - 해당 카드 ID에 매핑된 카드명만 AI에게 제공

2. **AI 분석**
   - 필터링된 카드 목록 중에서만 선택
   - 업무 내용과 카드명의 유사도 분석
   - 가장 적합한 카드 1개 선택

3. **폴백 처리**
   - 카테고리에 매핑된 카드가 없으면 전체 카드 제공
   - AI 응답 파싱 실패 시 "기타 업무" 카드 선택

### 예시

업무일지 테이블:
```
| 상태 | 카테고리 | 업무 내용 | 우선순위 | 난이도 | 소요시간 | 진도 | 예상 완료일 |
| ✅ 완료 | Redmine | #1234 버그 수정 | 긴급 | 중 | 2h | 100% | 2025-12-27 |
| 🔄 진행중 | 자동화테스트운영 | TC 시나리오 작성 | 중요 | 상 | 3h | 60% | 2025-12-30 |
```

처리 과정:
1. 두 행 모두 파싱 (상태 무관)
2. 첫 번째 행: 카테고리 = "Redmine"
3. `category.Redmine` = ["VZAS6bSk", "VHYpqMEd", "s4lnGdgS", "6c5cwIf0", "Lv1j08Ng"]
4. 해당 ID의 카드명만 AI에게 제공:
   - "Server-i Agent Smoke 자동화"
   - "Privacy-i MacOS Agent 자동화"
   - "Webkeeper Playwright 자동화"
   - "Server-i TestComplete 자동화"
   - "SQL Commit마다 스키마 생성/업데이트 비교 자동화"
5. AI가 위 5개 카드 중 가장 적합한 카드 선택
6. 선택된 카드에 댓글 추가 및 "진행 중" List로 이동
7. 두 번째 행도 동일하게 처리

**선택 우선순위:**
1. 업무 내용과 카드명이 정확히 일치
2. 키워드 기반 유사도
3. 기본값: "기타 업무" 카드

**중요:**
- 상태가 "완료"든 "진행중"이든 **모든 업무**를 Trello에 동기화
- 모든 카드를 무조건 "진행 중" List로 이동

---

## 🔄 다음 단계

1. n8n에서 워크플로우 테스트
2. AI 선택 정확도 모니터링
3. 필요시 프롬프트 튜닝
4. 주간보고서 자동화와 통합

---

## 📝 참고 자료

- [Trello API 문서](https://developer.atlassian.com/cloud/trello/rest/)
- [n8n 문서](https://docs.n8n.io/)
- [OpenAI API 문서](https://platform.openai.com/docs/)
