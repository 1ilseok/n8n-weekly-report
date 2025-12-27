# 초기 설정 가이드

처음 사용하는 사람을 위한 단계별 설정 가이드입니다.

## 목차

1. [사전 요구사항](#1-사전-요구사항)
2. [n8n 설치 및 실행](#2-n8n-설치-및-실행)
3. [OpenAI API 키 발급](#3-openai-api-키-발급)
4. [프로젝트 설정](#4-프로젝트-설정)
5. [워크플로우 임포트](#5-워크플로우-임포트)
6. [첫 실행 테스트](#6-첫-실행-테스트)

---

## 1. 사전 요구사항

### 필수 항목
- **Node.js** 18.x 이상 (또는 Docker)
- **OpenAI API 계정** (결제 수단 등록 필요)
- **macOS/Linux** (Windows는 WSL 권장)

### 설치 확인

```bash
# Node.js 버전 확인
node --version
# v18.0.0 이상이어야 함

# npm 버전 확인
npm --version

# Docker 설치 확인 (선택)
docker --version
```

---

## 2. n8n 설치 및 실행

### 방법 1: Docker 사용 (권장)

```bash
# n8n 컨테이너 실행
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=false \
  n8nio/n8n

# 실행 확인
docker ps | grep n8n
```

**접속**: http://localhost:5678

### 방법 2: npm 글로벌 설치

```bash
# n8n 설치
npm install -g n8n

# n8n 실행
n8n start

# 또는 환경변수 파일 지정하여 실행
n8n start --env-file=/path/to/.env
```

**접속**: http://localhost:5678

### 초기 설정

1. 브라우저에서 http://localhost:5678 접속
2. 계정 생성 (이메일, 비밀번호 입력)
3. 대시보드 확인

---

## 3. OpenAI API 키 발급

### Step 1: OpenAI 계정 생성

1. https://platform.openai.com/signup 접속
2. 이메일 또는 Google 계정으로 가입
3. 이메일 인증 완료

### Step 2: 결제 수단 등록

1. https://platform.openai.com/settings/organization/billing/overview 접속
2. **Add payment method** 클릭
3. 신용카드 정보 입력
4. 결제 한도 설정 (권장: $5-10/month)

> **참고**: API 사용량에 따라 과금됩니다. gpt-4o-mini는 저렴하지만 첫 달은 사용량을 모니터링하세요.

### Step 3: API 키 생성

1. https://platform.openai.com/api-keys 접속
2. **+ Create new secret key** 클릭
3. 키 이름 입력 (예: `n8n-weekly-report`)
4. **Create secret key** 클릭
5. 생성된 키 복사 (다시 볼 수 없으니 안전한 곳에 저장!)

**생성된 키 형식**: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 4. 프로젝트 설정

### Step 1: 프로젝트 다운로드

```bash
# 프로젝트 클론 (또는 ZIP 다운로드)
git clone <repository-url> n8n-weekly-report
cd n8n-weekly-report
```

### Step 2: 환경변수 설정

```bash
# .env.example 파일을 .env로 복사
cp .env.example .env

# .env 파일 편집
vim .env
# 또는
nano .env
```

**.env 파일 내용:**

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-actual-api-key-here

# n8n Configuration (선택사항)
# N8N_HOST=localhost
# N8N_PORT=5678
# N8N_PROTOCOL=http
```

**중요**: `OPENAI_API_KEY`에 Step 3에서 복사한 실제 API 키를 입력하세요.

### Step 3: 디렉토리 초기화

```bash
# 실행 권한 부여 (스크립트가 있는 경우)
# chmod +x setup.sh && ./setup.sh

# 또는 수동으로 디렉토리 생성
mkdir -p daily-worklogs/$(date +%Y-%m)
mkdir -p weekly-reports/$(date +%Y)

# 디렉토리 확인
tree -L 2
```

**예상 구조:**

```
n8n-weekly-report/
├── daily-worklogs/
│   └── 2025-01/           # 현재 월
├── weekly-reports/
│   └── 2025/              # 현재 연도
├── templates/
├── workflows/
├── .env                   # 생성됨
└── .env.example
```

---

## 5. 워크플로우 임포트

### Step 1: n8n UI 접속

브라우저에서 http://localhost:5678 열기

### Step 2: 워크플로우 가져오기

1. 왼쪽 메뉴에서 **Workflows** 클릭
2. 우측 상단 **⋮** (점 3개) 클릭
3. **Import from File** 선택
4. `workflows/weekly-report-generator.json` 파일 선택
5. **Import** 클릭

### Step 3: 환경변수 연결 확인

워크플로우가 임포트되면 자동으로 `{{$env.OPENAI_API_KEY}}`를 읽습니다.

**n8n에서 환경변수 사용 방법:**

#### Docker를 사용하는 경우

```bash
# 컨테이너 중지
docker stop n8n

# 환경변수 포함하여 재시작
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e OPENAI_API_KEY=sk-proj-your-actual-key-here \
  n8nio/n8n
```

#### npm 사용하는 경우

```bash
# .env 파일이 있는 디렉토리에서 실행
export OPENAI_API_KEY=sk-proj-your-actual-key-here
n8n start

# 또는 .env 파일 자동 로드 (direnv 사용)
direnv allow .
n8n start
```

### Step 4: 워크플로우 활성화

1. 워크플로우 상단의 **Inactive** 스위치를 **Active**로 변경
2. 저장 (Ctrl+S 또는 Save 버튼)

---

## 6. 첫 실행 테스트

### Step 1: 샘플 데일리 로그 생성

```bash
# 오늘 날짜로 샘플 파일 생성
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_MONTH=$(date +%Y-%m)

# 템플릿 복사
cp templates/daily-worklog-template.md daily-worklogs/$CURRENT_MONTH/$CURRENT_DATE.md

# 파일 편집
vim daily-worklogs/$CURRENT_MONTH/$CURRENT_DATE.md
```

**샘플 내용 (예시):**

```markdown
---
date: 2025-01-03
author: ilseok
trello_card_mapping:
  "card1": "https://trello.com/c/abc123"
---

# 250103 (금) 업무일지

## 📌 오늘 완료한 업무
| 카테고리 | 업무 내용 | 소요시간 | 난이도 |
|----------|-----------|----------|--------|
| Redmine | #1234 버그 수정 | 2h | 중 |
| WebKeeper | Playwright TC 작성 | 3h | 상 |
| 기타 | 회의 참석 | 1h | 하 |

## 🚧 진행 중인 업무
| 카테고리 | 업무 내용 | 진도 | 예상 완료일 |
|----------|-----------|------|-------------|
| Redmine | #1235 기능 개발 | 60% | 01/10 |

## 📋 내일 할 일
| 우선순위 | 업무 내용 | 예상 소요시간 |
|----------|-----------|---------------|
| 1 | #1235 기능 개발 계속 | 4h |

## ⚠️ 블로커/이슈
| 이슈 내용 | 영향도 | 해결 방안 |
|-----------|--------|-----------|
| 없음 | - | - |

## 💡 메모/학습
- n8n 워크플로우 학습 완료
```

### Step 2: 여러 날짜의 샘플 데이터 생성 (선택)

주간보고서 테스트를 위해서는 최소 2-3일의 데이터가 필요합니다:

```bash
# 지난 3일간의 샘플 생성
for i in {0..2}; do
  TARGET_DATE=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "-${i} days" +%Y-%m-%d)
  TARGET_MONTH=$(date -v-${i}d +%Y-%m 2>/dev/null || date -d "-${i} days" +%Y-%m)
  mkdir -p daily-worklogs/$TARGET_MONTH
  cp templates/daily-worklog-template.md daily-worklogs/$TARGET_MONTH/$TARGET_DATE.md
  echo "Created: daily-worklogs/$TARGET_MONTH/$TARGET_DATE.md"
done
```

### Step 3: 워크플로우 수동 실행

1. n8n에서 `weekly-report-generator` 워크플로우 열기
2. **수동 트리거 (주차 지정)** 노드 클릭
3. `target_week` 필드에 입력:
   - 형식: `YYYY-WW`
   - 예: `2025-01` (2025년 1주차)
4. 우측 상단 **Execute Workflow** 클릭
5. 실행 결과 확인

### Step 4: 결과 확인

```bash
# 생성된 주간보고서 확인
ls -la weekly-reports/2025/

# 내용 확인
cat weekly-reports/2025/2025-01.md
```

**예상 출력:**

```markdown
---
week_number: 1
year: 2025
start_date: 2025-01-03
end_date: 2025-01-09
author: ilseok
generated_at: 2025-01-10 08:15:23
---

# 2025년 1주차 주간보고 (01/03 ~ 01/09)

## 1. Redmine 일감
| 상태 | 일감번호 | 제목 | 담당자 | 비고 |
|------|----------|------|--------|------|
| 완료 | #1234 | 버그 수정 | ilseok | 2h 소요 |
| 진행중 | #1235 | 기능 개발 | ilseok | 60% 완료 |

...
```

---

## 트러블슈팅

### 1. n8n이 OpenAI API 키를 인식하지 못하는 경우

**증상**: `401 Unauthorized` 또는 `Invalid API Key` 오류

**해결 방법:**

```bash
# 환경변수 확인
echo $OPENAI_API_KEY

# Docker 재시작 (환경변수 포함)
docker stop n8n
docker rm n8n
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e OPENAI_API_KEY=your-actual-key-here \
  n8nio/n8n

# npm의 경우
export OPENAI_API_KEY=your-actual-key-here
n8n start
```

### 2. 워크플로우 실행 시 "파일을 찾을 수 없음" 오류

**증상**: `해당 주간의 업무일지를 찾을 수 없습니다`

**해결 방법:**

```bash
# 1. 디렉토리 존재 확인
ls -la daily-worklogs/

# 2. 샘플 파일 생성
mkdir -p daily-worklogs/$(date +%Y-%m)
cp templates/daily-worklog-template.md daily-worklogs/$(date +%Y-%m)/$(date +%Y-%m-%d).md

# 3. 워크플로우 재실행
```

### 3. n8n 접속이 안 되는 경우

**증상**: http://localhost:5678 접속 불가

**해결 방법:**

```bash
# Docker 상태 확인
docker ps -a | grep n8n

# 로그 확인
docker logs n8n

# 재시작
docker restart n8n

# npm의 경우
pkill -f n8n
n8n start
```

### 4. OpenAI API 비용 과다 발생

**예방 방법:**

1. OpenAI 대시보드에서 **Usage limits** 설정
   - https://platform.openai.com/settings/organization/limits
   - Hard limit: $10/month (권장)

2. 워크플로우를 자동 실행에서 수동 실행으로 변경:
   - n8n에서 워크플로우 **Inactive** 상태로 변경
   - 필요할 때만 수동으로 Execute

---

## 다음 단계

설정이 완료되었다면:

1. **일일 업무일지 작성 습관화**
   - 매일 퇴근 전 5분 투자
   - 템플릿 활용하여 빠르게 작성

2. **주간보고서 자동 생성 활성화**
   - 매주 금요일 08:00 자동 실행
   - 또는 필요할 때 수동 실행

3. **AI 프롬프트 커스터마이징**
   - `workflows/weekly-report-generator.json` 파일의 프롬프트 수정
   - 회사 양식에 맞게 조정

4. **추가 워크플로우 활용 (선택)**
   - `daily-to-trello.json`: 일일 업무를 Trello 카드로 자동 등록
   - Slack, Mattermost 연동 추가

---

**설정 완료를 축하합니다!** 🎉

문제가 발생하면 [README.md](README.md)의 트러블슈팅 섹션을 참고하세요.
