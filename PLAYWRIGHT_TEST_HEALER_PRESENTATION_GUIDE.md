# 🤖 Playwright Test Healer 개발 여정 및 발표 종합 가이드

> **본 문서는 Playwright 소스코드 Self-Healing 시스템(Test Healer)의 개발 여정, 사내 로컬 LLM 인프라 전환 과정, 소스코드 및 아키텍처 명세, 그리고 긍정적 성과와 비판적 한계점을 종합적으로 입체 분석한 발표용 통합 가이드 문서입니다.**

---

## 📌 1. 발표 개요 및 제목 제안 (Presentation Titles)

### 1.1 발표 핵심 카피 & 메시지
* **핵심 메시지**: 과거 Cursor IDE 기반의 수동/반자동 디버깅에서 벗어나, **개발자 및 IDE 개입 0%의 CI/CD 무인(Unattended) 자율 힐링 파이프라인**으로 진화.
* **한 줄 요약**: "진단·수정·재검증은 100% 완전 자율, 안전을 위한 최종 승인만 인간이 맡는 실무형 자율 힐링 파이프라인"

### 1.2 관점별 대표 발표 제목 (10선)

| 번호 | 관점 / 콘셉트 | 발표 제목 및 부제 |
| :--- | :--- | :--- |
| **1** | **IDE 탈피 (추천 ⭐)** | **Cursor를 넘어 CI/CD로: IDE 개입 없이 스스로 코드를 고치는 Playwright Self-Healing 여정**<br>*부제: IDE 수동 명령에서 Jenkins 기반 무개입 완전 자동 힐링 에이전트로의 진화* |
| **2** | **완전 자율화 강조** | **"더 이상 IDE를 열지 마세요" — 100% 자율 구동되는 Playwright Test Healer 구축기**<br>*부제: IDE 개발자 개입 제로, CI/CD 파이프라인 속에서 스스로 판단하고 치유하는 AI 에이전트* |
| **3** | **기술 진화 (Journey)** | **Cursor의 AI 도우미에서 무인 자율 에이전트까지: Playwright Test Healer 발전사**<br>*부제: 로컬 LLM 검증부터 DGX Spark 인프라 최적화, 그리고 다중 제품 Orchestration까지* |
| **4** | **엔터프라이즈 확장** | **IDE 수동 힐링에서 엔터프라이즈 무인 오케스트레이션으로**<br>*부제: Playwright 소스코드 Self-Healing 시스템의 개발 및 내재화 여정* |
| **5** | **에이전틱 AI (Agentic)** | **human-in-the-loop 탈피: Playwright 자율 셀프힐링 에이전트 구축 기술**<br>*부제: MCP 프록시와 로컬 LLM을 결합한 백그라운드 무인(Unattended) 에이전트 루프* |
| **6** | **파이프라인 통합** | **IDE의 한계를 넘어서: CI/CD 파이프라인에서 작동하는 Agentic Playwright Healer**<br>*부제: AI 에이전트가 직접 디버깅하고 검증까지 완결짓는 무인 QA 파이프라인* |
| **7** | **사내 LLM 내재화** | **사내 로컬 LLM으로 완성한 Zero-IDE 기반 Playwright Test Healer**<br>*부제: vLLM, Mac Studio, DGX Spark(Qwen 27B)를 거치며 완성한 사내 자율 QA 에이전트* |
| **8** | **인프라 최적화** | **외부 API와 IDE 없이 동작하는 100% 사내 인프라 기반 Self-Healing QA 시스템**<br>*부제: DGX Spark(128GB) FP8 최적화와 Jenkins가 만난 자율형 AI 힐링 파이프라인* |
| **9** | **운영 효율성 (ROI)** | **밤사이에 스스로 유지보수되는 QA 자동화: 무인 Playwright Test Healer**<br>*부제: IDE 실행 없이 빌드 실패를 감지·수정·재검증하는 AI 에이전트 도입기* |
| **10** | **유지보수 혁신** | **QA 유지보수 제로(Zero-Maintenance)를 향해: IDE 없이 움직이는 AI 힐링 시스템**<br>*부제: 다중 제품(Webkeeper, EDR 등) 테스트 자동화 라인에 적용된 AI Self-Healing 여정* |

---

## 📑 2. 발표 슬라이드 목차 및 세부 구성 (Slide Outline)

```text
[Slide 1] 표지: 제목 및 발표 개요 (IDE 탈피 선언)
[Slide 2] Executive Summary: IDE 탈피와 무인 CI/CD 파이프라인 구축 요약
[Slide 3] 배경 및 문제 정의: E2E 테스트 Flakiness와 스크립트 유지보수 병목
[Slide 4] [여정 1] 사내 로컬 LLM & HW 인프라 검증기 (vLLM → Mac Studio → DGX Spark)
[Slide 5] [여정 2] LLM 양자화 & 모델 벤치마크 (Qwen 3.6 27B vs Gemma 4 31B, BF16/FP8)
[Slide 6] [기술 1] IDE 탈피! Pi Agent & MCP 기반 무인 자율 구동 아키텍처
[Slide 7] [기술 2] 에이전트 의사결정 정책 & 가드레일 (Decision Matrix & Anti-Fake)
[Slide 8] [기술 3] 사고 과정(Thinking Process) 시각화 & Interactive HTML Dashboard
[Slide 9] [확산] 엔터프라이즈 오케스트레이션 & 다중 제품 확장 (Jenkins Orchestrator)
[Slide 10] 입체적 평가 및 향후 발전 로드맵 (Strengths vs Limitations & Future Roadmap)
```

### 멘트 및 데모 배치 가이드
* **Slide 1 & 2**: 이전 발표(Cursor IDE 내 수동 질문) 화면과 현재(Jenkins 무인 파이프라인)의 대비 캡처를 대치 배치하여 "IDE 탈피" 시각화.
* **Slide 6 & 8**: `extract_thinking.js`로 생성된 HTML 대시보드 및 Mattermost 카드 알림 캡처 화면을 시연 형태로 포함.

---

## 📅 3. 타임라인별 상세 개발 여정 (Detailed Timeline)

```text
2026.02          2026.03          2026.04~06        2026.07          2026.08          2026.09
  │                │                  │                │                │                │
  ├─ 힐링 아이디어 ├─ Playwright      ├─ Mac Studio    ├─ Healer 개발   ├─ DGX Spark     ├─ Ubuntu 전환
  │  탐색 (Medium)    Agent 연구        30B 샌드박스     공식 착수 (7/14)   최적화           ├─ 리포트 저장소 분리
  └─ Cursor/MCP    └─ vLLM Tool Call  └─ HW 도입 근거    ├─ Pi + MCP 연결 ├─ v1.0 배포      └─ Central
     초기 검토        이슈 발굴          마련 연구        └─ Thinking 파서 └─ 실제 제품 적용   Orchestrator
```

### 3.1 Phase 1. 개념 정립 및 초기 연구 (2026년 2월 ~ 3월)
* **2월 중순**: 팀장님 공유 아티클(*Build your own Playwright test healer with AI agents*) 바탕으로 AI Healer 개념 수립. `Playwright MCP + Cursor` 기반 디버깅 검토.
* **3월 초~중순**: Playwright Agent(Planner, Generator, Healer) 소스 분석. Claude 3.5 Sonnet API 및 Copilot Pro를 구매하여 힐링 성능 Benchmark 확보.
* **3월 말**: 사내 vLLM 서버 연동 시도 시 **Tool Calling(도구 호출) 미지원/오류** 확인. 로컬 LLM을 위한 커스텀 에이전트 프록시의 필요성 입증.

### 3.2 Phase 2. 사내 LLM 하드웨어 타당성 연구 (2026년 4월 ~ 6월)
* **4월 초**: 팀장님과 논의 — **"Mac Studio + LM Studio + 30B 모델"** 환경을 구축하여 하드웨어 구매 명세 및 근거(Justification) 마련을 위한 샌드박스 테스트 진행. (특정 단일 모델명이 아닌 30B급 체급 모델 검증)
* **4월~5월**: OpenCode/Pi 연결 시도 및 Context Window(32K) 제약과 압축(Compaction)에 따른 지능 저하 현상 도출.

### 3.3 Phase 3. Test Healer Agent 프로토타입 개발 (2026년 7월)
* **7/14**: **Test Healer 개발 공식 착수** (최초 plan 및 구현 명세서 작성).
* **7/15~7/16**: `pi + 로컬 LLM` 환경에서 `.pi/HEALER_PROMPT.md` 기반 Healer Agent 동작 성공.
* **7/21**: `test-results/junit.xml` 파싱으로 실패 TC 타겟팅 및 BDD `.spec.ts` 역추적 로직 개발.
* **7/23**: **에이전트 프롬프트 & 가드레일 정립 (`playwright-test-healer.agent.md`)**:
  * Step 0 Pre-flight Check (MCP 연결 사전 확인)
  * 파일 보호 범위 설정 (`features/` 수정 금지, `tests/*.spec.ts`만 수정)
  * 최대 재시도 3회 제한 및 토큰 절약 규칙 반영
* **7/24**: 세션 로그 파서(`extract_thinking.js`) 및 장애 주입 시나리오(`HEALING_TEST_SCENARIOS.md`) 작성.

### 3.4 Phase 4. DGX Spark 인프라 최적화 & v1.0.0 정식 배포 (2026년 8월)
* **8/3~8/5**: 사내 Qwen-3.6-27B-Fable 모델 사용 시 검증 실행 지연 분석 및 `child-process.js` 패치. `playwright-test_test_debug` 사용 후 브라우저 프로세스가 남아있는 **Lifecycle 누락 문제** 발굴 및 프로세스 강제 종료 로직 추가.
* **8/6**: **DGX Spark (128GB) 인프라 최적화 & 모델 벤치마크**:
  * VRAM pre-allocation (KV Cache 선점) 메커니즘 해석.
  * Qwen 27B 모델의 Tool Calling 지연 및 JSON 포맷팅 오류 발굴 후 **gemma4:31b-it-qat (96K Context)** 모델 최종 채택.
* **8/11**: `playwright-test-agents` SCM 리포지토리 생성 및 `Jenkinsfile.healer` 파이프라인 구축 (`gemma4:31b-it-qat` 바인딩).
* **8/12**: 단일 TC 순차 힐링 루프(`extract_failed_tests.js`) 및 대시보드 UI 전면 개편.
* **8/13**: **🎉 Playwright Test Healer v1.0.0 정식 배포 및 메터모스트 공지**.
* **8/14~8/31**: 실제 제품 자동화 라인(`Webkeeper`, `EDR`, `Mail-i`, `Privacy-i`, `DB-i`) 적용.

### 3.5 Phase 5. 크로스 플랫폼 & 엔터프라이즈 Orchestrator 확산 (2026년 9월)
* **9/2~9/4**: Ollama 로그 분석으로 JSON 문법 규격화. 가짜 힐링 방지를 위한 `FLAKY_PASSED` 및 불변성 원칙 도입.
* **9/7~9/14**: **Ubuntu Linux 크로스 플랫폼 전환** (Windows 실행 환경에서 Ubuntu Headless 환경으로 대통합).
* **9/15~9/18**: **`healer-reports` 독립 리포지토리 분리** 및 Mattermost PAT Token 기반 카드 알림 구축.
* **9/21~9/28**: **중앙 집중식 Orchestrator 파이프라인 (`Jenkins.orchestrator`) 구축**으로 다중 제품 자동 스케줄링.

---

## 🖥️ 4. 사내 로컬 LLM & 인프라 최적화 분석 (LLM Infrastructure)

### 4.1 인프라 전환 및 평가 요약

| 단계 | 인프라 / 장비 | 서빙 엔진 | 핵심 결과 및 분석 |
| :--- | :--- | :--- | :--- |
| **1단계** *(3월)* | 사내 vLLM 서버 | vLLM (API) | Continue/Cline 연동 시 Tool Calling 규격 미지원 발견 |
| **2단계** *(4~6월)*| 팀 Mac Studio | LM Studio / Ollama | 30B 체급 모델 샌드박스 구동, Context 32K 한계 도출 |
| **3단계** *(8월)* | **DGX Spark (128GB)**| Ollama / vLLM | KV Cache pre-allocation 해석. Qwen 27B Tool Call 오류 파악 후 **gemma4:31b-it-qat 검증** |
| **4단계** *(8~9월)*| Ollama / Pi Agent | Ollama API / Pi CLI | **gemma4:31b-it-qat (96K Context)** 최종 채택 & 실운영 적용, JSON 규격화 완숙 |

### 4.2 모델 벤치마크 및 양자화(Quantization) 전략

```text
[DGX Spark 128GB Unified Memory]
 ├── qwen3-coder:30b-a3b-q4_K_M : 30B Coder 후보 모델 (Mac Studio PoC / Ollama 검증)
 ├── Qwen-3.6-27B-Fable       : 사내 범용 모델 (child-process 실행 지연 발생)
 └── gemma4:31b-it-qat        : RFC JSON Tool Calling 완벽 준수 + 96K 대용량 Context 지원 ➔ 최종 실운영 채택! ⭐
      ├── VRAM 소모             : QAT(Quantization-Aware Training) 모델로 VRAM 및 추론 속도 최적화
      └── 특징                 : 학습 단계 양자화 적용으로 4비트 수준 용량에서 원본급 지능 및 도구 호출 정밀도 보존
```

---

## 🏗️ 5. 핵심 소스코드 및 아키텍처 명세 (`playwright-test-agents`)

### 5.1 동적 환경 생성 스크립트 (`setup-pi.ps1`)
젠킨스 에이전트 실행 시 루트 워크스페이스의 `.pi/` 디렉터리에 실행 환경 설정 파일 3개를 동적 생성:
1. `.pi/models.json`: 사내 Ollama 엔드포인트(`http://10.226.50.2/v1`) 및 모델 지정.
2. `.pi/mcp.json`: `@playwright/test/cli.js run-test-mcp-server` 바인딩, `requestTimeoutMs: 3600000`(1시간) 주입.
3. `.pi/settings.json`: Context Compaction (`reserveTokens: 12000`, `keepRecentTokens: 8000`) 설정.

### 5.2 실패 TC 핀포인트 추출기 (`extract_failed_tests.js`)
* `test-results/junit.xml` 내 `<failure>`/`<error>` 파싱.
* `npx playwright test "<spec>" --list --reporter=json`을 백그라운드 실행하여 유일한 Playwright `testId`와 `specFile`을 매핑한 `failed_tests.json` 생성.

### 5.3 에이전트 지침 및 Decision Matrix (`playwright-test-healer.agent.md`)
* **3대 Root Cause 분류**:
  * **Script Bug**: 코드 수정 (`edit`) $\rightarrow$ 재검증 (`test_run`) $\rightarrow$ `HEALED`
  * **Environment/Data Issue**: 코드 수정 금지 $\rightarrow$ `SKIPPED_ENV_ISSUE`
  * **Application Bug**: 코드 수정 금지 $\rightarrow$ `SKIPPED_APP_BUG`
* **엄격한 가드레일**: `features/` 수정 엄격 금지, `read` 시 `offset/limit` 필수, `playwright_test_test_list` 호출 금지.

### 5.4 사고 과정 시각화 리포터 (`extract_thinking.js`)
* 백그라운드 구동 중 AI가 남긴 `.jsonl` 세션 로그에서 Thinking Process, Token 사용량, Executed Tools를 파싱.
* 젠킨스 빌드 메뉴에 게시되는 **Interactive HTML Dashboard** (`index.html`) 생성.

### 5.5 다중 제품 오케스트레이터 (`Jenkinsfile.orchestrator` & `commit_and_report.js`)
* 매일 자정, 사내 다중 제품(`Webkeeper`, `EDR`, `Mail-i`, `Privacy-i`, `DB-i`)의 힐링을 순차 실행.
* 실패 TC가 0건일 경우 Heavy Stage를 즉시 스킵하여 리소스 절약.
* 제품 코드 저장소를 더럽히지 않고 `healer-reports` 전용 독립 저장소에 리포트만 푸시.

---

## ⚖️ 6. 입체적 시스템 평가: 긍정적 성과 vs 비판적 한계

```text
               ┌─────────────────────────────────────────┐
               │    Playwright Test Healer 입체 평가     │
               └────────────────────┬────────────────────┘
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          ▼                                                   ▼
【 긍정적 성과 (Strengths) 】                       【 차기 고도화 과제 (Improvement Tasks) 】
 1. IDE 탈피 100% 자율 파이프라인 (Auto-Commit 완비)   1. 메인 브랜치 Auto-PR/Merge 연동 가이드
 2. 촘촘한 가드레일 (Anti-Fake Healed)               2. 단순 스크립트 결함 외 BDD 대응 확장
 3. 사내 DGX Spark 원본 가동 (API 비용 $0)           3. 로컬 LLM의 포맷 붕괴 및 속도 개선
 4. 다중 제품 Orchestration 확장성                   4. GPU 병렬 큐 확장 파이프라인 구축
```

### 6.1 긍정적 성과 (Strengths)
1. **IDE 탈피 및 100% 무인 자율화**: 빌드 실패 감지, 원인 분석, 코드 수정, 재검증, **수정 결과 Auto-Commit/Push 및 Mattermost 카드 알림까지 백그라운드 100% 자율 완결** (자율성 평점 **5.0 / 5.0** 달성).
2. **강력한 가드레일 (Safety)**: BDD 시나리오 보호, 환경/제품 버그 스킵, `FLAKY_PASSED` 분리로 가짜 힐링 완벽 차단.
3. **인프라 비용 0원 & 최적화**: 상용 API 비용 없이 사내 DGX Spark 128GB 메모리를 활용해 BF16/FP8 원본 모델 가동.
4. **엔터프라이즈 확장성**: 크로스 플랫폼(Ubuntu) 지원 및 Central Orchestrator를 통한 다중 제품 라인 확장.

### 6.2 차기 고도화 과제 (Improvement Tasks)
1. **Auto-PR / Auto-Merge 연동**: 현재 구현된 Auto-Commit/Push에서 나아가, 메인 브랜치 직연동 시 안전한 승인 절차를 위한 PR 검토 가이드 보강.
2. **수정 범위의 확장**: 단일 `.spec.ts` 내 1차원적 결함 수정을 넘어, 복잡한 상태 의존성 및 BDD 시나리오 변경 건에 대한 대응력 확장.
3. **로컬 LLM 속도 개선**: 27B 로컬 LLM의 간헐적 포맷 붕괴(`INCOMPLETE_SESSION`) 방지 및 추론 속도 최적화.
4. **GPU 병렬 큐 확장**: 사내 GPU 자원 확충을 통해 단일 공유 큐의 순차 구동 병목 해소.

### 6.3 종합 판정 카피 및 향후 로드맵
> **"단순 실패 수정·재검증·자동 커밋/푸시 및 오케스트레이션까지 100% 자율화가 완비되었으며, 로컬 LLM 추론 속도 최적화 및 메인 브랜치 Auto-PR 연동을 차기 고도화 과제로 추진 중임."**

* **향후 개선 로드맵**:
  1. **Auto-PR / Auto-Merge 연동**: 신뢰도가 검증된 힐링 건에 대해 Git Pull Request 자동 생성 기능 추가.
  2. **병렬 큐 확장**: DGX Spark 자원 분배를 통한 제품별 병렬 힐링 파이프라인 구축.
