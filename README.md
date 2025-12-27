# n8n Weekly Report Generator

일일 업무일지를 수집하여 **AI로 자동 통합 및 분석**하여 주간보고서를 생성하는 n8n 워크플로우

## 주요 기능

- 일일 업무일지 자동 수집 (금요일 ~ 목요일, 7일간)
- AI 기반 업무 통합 및 중복 제거
- 카테고리별 자동 분류 (Redmine, 자동화, 기타)
- 시간 집계 및 통계 생성
- 주요 성과 자동 선별
- 특이사항 자동 감지

## 프로젝트 구조

```
n8n-weekly-report/
├── README.md
├── .env.example                        # 환경변수 설정 예시
├── workflows/
│   ├── weekly-report-generator.json    # 메인 워크플로우 (AI 기반)
│   ├── daily-to-trello.json           # (선택) 일일 업무를 Trello로 전송
│   └── weekly-report.json             # (레거시) Trello 기반 워크플로우
├── templates/
│   ├── daily-worklog-template.md      # 일일 업무일지 양식
│   └── weekly-report-template.md      # 주간보고서 양식 (참고용)
├── daily-worklogs/
│   └── YYYY-MM/                       # 일일 업무일지 저장 (월별 디렉토리)
│       └── YYYY-MM-DD.md
└── weekly-reports/
    └── YYYY/                          # 주간보고서 저장 (연도별 디렉토리)
        └── YYYY-WW.md
```

## 워크플로우 구성

### 메인 워크플로우: `weekly-report-generator.json`

```
[스케줄 트리거] 매주 금요일 08:00
        ↓
[수동 트리거] 특정 주차 지정 가능 (YYYY-WW)
        ↓
    [주차 계산]
    - 금요일 기준 주차 계산
    - 지난주 금요일 ~ 이번주 목요일 날짜 범위 계산
    - 해당 기간의 일일 업무일지 파일 목록 생성
        ↓
  [업무일지 파싱]
  - 7일간의 일일 업무일지 읽기
  - 완료 업무, 진행중 업무, 다음주 계획 추출
        ↓
 [AI 주간보고서 생성] (OpenAI gpt-4o-mini)
 - 중복 업무 통합 (같은 Redmine 일감 번호)
 - 시간 집계 (같은 업무의 총 소요 시간 합산)
 - 카테고리별 분류
 - 주요 성과 선별 (시간/난이도 기준)
 - 특이사항 자동 감지
        ↓
 [주간보고서 저장]
 - weekly-reports/YYYY/YYYY-WW.md 저장
```

## 설정 방법

### 1. 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
# OPENAI_API_KEY=sk-...your-api-key...
```

**OpenAI API 키 발급:**
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. 생성된 키를 `.env` 파일에 복사

### 2. n8n에서 워크플로우 가져오기

1. n8n 접속 (http://localhost:5678)
2. **Workflows** > **Import from File**
3. `workflows/weekly-report-generator.json` 선택
4. 워크플로우 **Active** 상태로 변경

### 3. 디렉토리 생성

```bash
# 일일 업무일지 저장 디렉토리
mkdir -p daily-worklogs/$(date +%Y-%m)

# 주간보고서 저장 디렉토리
mkdir -p weekly-reports/$(date +%Y)
```

## 사용 방법

### 1. 일일 업무일지 작성

매일 업무 종료 시 `templates/daily-worklog-template.md`를 참고하여 작성:

```bash
# 오늘 날짜로 파일 생성
cp templates/daily-worklog-template.md daily-worklogs/$(date +%Y-%m)/$(date +%Y-%m-%d).md

# 편집
vim daily-worklogs/$(date +%Y-%m)/$(date +%Y-%m-%d).md
```

**일일 업무일지 양식:**

| 섹션 | 내용 |
|------|------|
| **완료한 업무** | 카테고리, 업무 내용, 소요시간, 난이도 |
| **진행 중인 업무** | 카테고리, 업무 내용, 진도, 예상 완료일 |
| **내일 할 일** | 우선순위, 업무 내용, 예상 소요시간 |
| **블로커/이슈** | 이슈 내용, 영향도, 해결 방안 |
| **메모/학습** | 자유 형식 |

**카테고리 예시:**
- `Redmine` - 일감 번호 포함 (예: #1234)
- `Server-i` - TestComplete 관련 업무
- `WebKeeper` - Playwright 관련 업무
- `PV`, `macOS`, `기타 자동화`
- `인프라`, `문서화`, `회의`, `학습`

### 2. 주간보고서 자동 생성

#### 자동 실행 (스케줄)
- 매주 금요일 08:00에 자동 실행
- 지난주 금요일 ~ 이번주 목요일 데이터 수집

#### 수동 실행 (특정 주차 지정)
1. n8n에서 `weekly-report-generator` 워크플로우 열기
2. **수동 트리거** 노드에서 `target_week` 입력
   - 형식: `YYYY-WW` (예: `2025-01`)
3. **Execute Workflow** 클릭

#### 생성된 보고서 확인
```bash
# 최신 주간보고서 확인
ls -lt weekly-reports/$(date +%Y)/ | head -5

# 내용 확인
cat weekly-reports/2025/2025-01.md
```

### 3. 주간보고서 양식

AI가 다음 형식으로 자동 생성합니다:

```markdown
---
week_number: 1
year: 2025
start_date: 2025-01-03
end_date: 2025-01-09
author: ilseok
generated_at: 2025-01-10 08:00:00
---

# 2025년 1주차 주간보고 (01/03 ~ 01/09)

## 1. Redmine 일감
| 상태 | 일감번호 | 제목 | 담당자 | 비고 |
|------|----------|------|--------|------|
| ... | ... | ... | ... | ... |

## 2. 자동화 테스트
| 상태 | 분류 | 업무 내용 | 비고 |
|------|------|-----------|------|
| ... | ... | ... | ... |

## 3. 기타 업무
| 상태 | 분류 | 업무 내용 | 비고 |
|------|------|-----------|------|
| ... | ... | ... | ... |

## 4. 다음 주 계획
| 우선순위 | 분류 | 업무 내용 | 예상 완료일 |
|----------|------|-----------|-------------|
| ... | ... | ... | ... |

## 5. 주간 요약
### 통계
- 총 작업 시간: XX시간
- 완료한 업무: XX건
- 진행 중인 업무: XX건

### 주요 성과
- ...

### 특이사항
- ...
```

## AI 자동화 기능

### 1. 중복 업무 통합
같은 Redmine 일감 번호가 여러 날 나타나면 자동으로 하나로 통합하고 총 소요 시간을 합산합니다.

**예시:**
- 월요일: #1234 버그 수정 (2h)
- 화요일: #1234 버그 수정 테스트 (1h)
- 수요일: #1234 버그 수정 완료 (0.5h)

→ **결과**: #1234 버그 수정 및 테스트 완료 (3.5h)

### 2. 상태 업데이트
진행 중이던 업무가 완료로 바뀐 경우 최신 상태를 반영합니다.

### 3. 카테고리 자동 분류
- **Redmine 일감**: `#` 번호 자동 인식
- **자동화 테스트**: Server-i, WebKeeper, PV 등으로 세분화
- **기타 업무**: 인프라, 문서화, 회의, 학습 등

### 4. 주요 성과 선별
- 소요 시간이 긴 업무
- 난이도가 높은 업무
- 중요한 마일스톤 달성
→ AI가 자동으로 3-5개 선별

### 5. 특이사항 자동 감지
- 예상치 못한 이슈 발생
- 일정 지연 위험
- 중요한 기술적 결정
→ 블로커/이슈 섹션 분석하여 자동 작성

## 트러블슈팅

### n8n에서 환경변수를 인식하지 못하는 경우

```bash
# n8n 재시작
docker restart n8n

# 또는 .env 파일 경로 명시하여 실행
n8n start --env-file=/path/to/.env
```

### 특정 주차 보고서가 생성되지 않는 경우

1. 해당 주간의 일일 업무일지가 있는지 확인:
   ```bash
   ls daily-worklogs/YYYY-MM/
   ```

2. 워크플로우 로그 확인 (n8n UI):
   - **Executions** 탭에서 실행 기록 확인
   - 오류 메시지 확인

3. 수동으로 주차 지정하여 재실행:
   - `target_week` 입력: `2025-01`

### AI 생성 결과가 이상한 경우

1. OpenAI API 키 확인:
   ```bash
   echo $OPENAI_API_KEY
   ```

2. 프롬프트 조정 (workflows/weekly-report-generator.json:84):
   - `temperature` 값 조정 (현재 0.3, 범위: 0.0 ~ 1.0)
   - 낮을수록 일관성 높음, 높을수록 창의적

3. 모델 변경:
   - `gpt-4o-mini` → `gpt-4o` (더 정확하지만 비용 증가)

## 기여 및 라이선스

이 프로젝트는 개인 업무 자동화를 위해 작성되었습니다.
자유롭게 수정하여 사용하세요.

## 관련 문서

- [일일 업무일지 템플릿](templates/daily-worklog-template.md)
- [주간보고서 템플릿 (참고용)](templates/weekly-report-template.md)
- [n8n 공식 문서](https://docs.n8n.io/)
- [OpenAI API 문서](https://platform.openai.com/docs/api-reference)
