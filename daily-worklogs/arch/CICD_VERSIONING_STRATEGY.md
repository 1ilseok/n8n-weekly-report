# AQA Portal - 버전 관리 및 CI/CD 파이프라인 구축 제안서

본 문서는 `aqa-portal` 프로젝트(FastAPI + React + Docker)의 안정적인 서비스 운영과 개발 생산성 향상을 위한 **버전 관리 전략** 및 **자동화된 배포(CI/CD) 환경 구축 방안**을 제안합니다. 팀 내 인프라 환경과 요구사항에 맞춰 최적의 방안을 결정하기 위한 논의 자료로 활용하시기 바랍니다.

---

## 1. 버전 관리 및 브랜치 전략

개발 환경과 운영(배포) 환경을 안전하게 분리하는 가장 기초적인 단계입니다.

### 1.1. 버전 표기법 (Semantic Versioning)
표준적인 `MAJOR.MINOR.PATCH` 방식을 채택합니다.
* **운영 배포용:** `v1.0.0`, `v1.2.1` 등 Git Tag로 관리
* **개발 빌드용:** `v1.2.0-dev`, `commit-hash` (예: `dev-abc123f`) 등

### 1.2. 브랜치 전략 (Git Flow / GitHub Flow 변형)
* **`main` (운영 환경):**
  * 언제든 배포 가능한, 검증된 코드만 존재합니다.
  * 코드가 병합될 때 반드시 `vX.Y.Z` 형태의 Git Tag를 생성하여 버전을 고정합니다.
* **`develop` (개발/테스트 환경):**
  * 다음 릴리스를 위해 기능들이 통합되는 브랜치입니다.
  * 이 브랜치에 코드가 푸시되면 개발 서버로 즉시 자동 배포(Dev Deploy)됩니다.
* **`feature/...` (기능 개발):**
  * 개별 기능 개발을 위한 브랜치로, 작업 완료 후 `develop`으로 Merge Request(Pull Request)를 요청합니다.

### 1.3. 코드 레벨 버전 명시
빌드된 산출물(UI 및 API 응답)에서 현재 버전을 쉽게 확인할 수 있도록 구성합니다.
* **프론트엔드 (React/Vite):** `package.json`의 version을 `vite.config.ts`를 통해 환경변수로 주입하여 화면(Footer 등)에 노출.
* **백엔드 (FastAPI):** `backend/config.py`에 버전을 명시하여 `/docs` (Swagger) 및 `/api/health` 엔드포인트에 노출.

---

## 2. Docker 빌드 및 배포 분리 전략

현재 존재하는 2개의 Docker Compose 파일을 목적에 맞게 완전히 분리하고, CI/CD에 적합하게 구조를 개선합니다.

* **개발용 (`docker-compose.dev.yml`)**
  * **목적:** 로컬 개발 및 개발(Dev) 서버 구동
  * **특징:** 소스코드를 Volume으로 마운트하여 Hot Reload(수정 즉시 반영) 지원. 별도의 이미지 빌드 과정을 최소화.
* **운영용 (`docker-compose.yml`)**
  * **목적:** 프로덕션(Prod) 서버 구동
  * **특징:** 컨테이너 내부에서 코드를 빌드하지 않음. CI/CD 파이프라인에서 이미 빌드되어 레지스트리에 저장된 **완제품 도커 이미지(Tag 명시)를 Pull 받아서 실행만 수행**.

---

## 3. CI/CD 파이프라인 아키텍처 (공통 흐름)

어떤 도구를 선택하든 다음 4단계(Stages) 파이프라인을 구축하는 것을 목표로 합니다.

1. **Test (검증):** 코드 푸시 시 린트(ESLint, Ruff 등) 및 단위 테스트(Pytest, Vitest) 실행.
2. **Build & Push (도커 굽기):** 검증을 통과한 코드를 Docker 이미지로 빌드하고, Container Registry(GitLab Registry, Docker Hub, Harbor 등)에 업로드.
3. **Deploy (배포):** 대상 서버(Dev/Prod)에 접속하여 새 이미지를 Pull 받고 `docker-compose up -d` 수행.
4. **Notify (알림):** 배포 성공/실패 여부를 팀 메신저(Mattermost 등)로 알림.

---

## 4. 파이프라인 도구 제안 및 비교

팀 내 인프라 환경과 기술 스택 선호도에 따라 아래 두 가지 방안 중 하나를 선택할 수 있습니다.

### 제안 A: GitLab CI/CD 기반 자동화 (추천)
현재 소스코드를 GitLab에서 관리 중이거나 이전할 계획이라면 가장 구축이 빠르고 매끄러운 방법입니다.

* **장점:**
  * 소스코드 저장소와 CI/CD가 통합되어 있어 관리가 매우 직관적입니다.
  * 기본 제공되는 **GitLab Container Registry**를 사용하여 도커 이미지를 무료/안전하게 저장할 수 있습니다.
  * YAML(`.gitlab-ci.yml`) 파일 하나로 파이프라인의 모든 코드를 버전 관리할 수 있습니다.
* **작동 방식:**
  * `develop` 푸시 -> `Test` -> `Build (Tag: dev-hash)` -> `Dev 서버 자동 배포`
  * `v1.2.0` 태그 푸시 -> `Test` -> `Build (Tag: v1.2.0, latest)` -> `Prod 서버 자동 배포`

### 제안 B: Jenkins 기반 자동화
사내에 이미 Jenkins 인프라가 구축되어 있거나, 파이프라인을 세밀하게 제어해야 하는 경우 적합합니다.

* **장점:**
  * 막강한 플러그인 생태계를 통해 어떤 복잡한 환경이나 도구와도 연동이 가능합니다.
  * 다양한 프로젝트의 빌드/배포 상태를 중앙 대시보드에서 관리하기 좋습니다.
* **작동 방식:**
  * 프로젝트 루트에 `Jenkinsfile`을 작성하여 Pipeline as Code 구현.
  * GitLab Webhook을 통해 Jenkins 트리거.
  * 배포 안전성을 위해 운영 배포의 경우, Jenkins UI에서 배포할 **태그 버전(v1.2.0)을 직접 선택(Build with Parameters)하여 수동 트리거**하는 방식을 추천.

---

## 5. 기존 자산 마이그레이션 및 적용 방안

자동화 파이프라인이 도입되면 기존 프로젝트 구조의 일부 역할이 변경되어야 합니다.

1. **`deploy.py`의 역할 변경 (Release Helper Tool)**
   * 기존: 직접 서버에 코드를 풀고 도커 컨테이너를 재시작하는 스크립트.
   * 변경 후: 개발자가 릴리스를 준비할 때 버전을 올리고(Version Bump) Git 태그를 자동으로 생성하여 원격 저장소에 푸시(Push)해 주는 유틸리티 스크립트로 변경. (실제 배포는 푸시된 태그를 인식한 CI/CD가 수행)
2. **환경변수 (시크릿) 관리**
   * DB 패스워드, JWT Secret 키 등은 `.env` 파일로 Git에 올리지 않습니다.
   * GitLab CI/CD Variables 또는 Jenkins Credentials에 등록하여, 파이프라인이 배포 단계에서 서버에 `.env` 파일을 동적으로 생성하도록 변경해야 합니다.

---

## 6. 팀 논의 권장 사항 (Next Steps)

성공적인 도입을 위해 팀 회의에서 다음 항목들을 결정해 주시길 권장합니다.

1. **버전/브랜치 전략:** 본 문서의 브랜치(main/develop) 및 Tag(v1.0.0) 기반 배포 전략에 동의하는가?
2. **CI/CD 플랫폼 선택:** 기존 사내 인프라를 고려했을 때 GitLab CI/CD와 Jenkins 중 어느 것을 사용할 것인가?
3. **도커 레지스트리:** 빌드된 도커 이미지를 어디에 보관할 것인가? (GitLab Registry, Docker Hub, 사내 구축 Registry 등)
4. **시크릿 관리:** 운영 환경의 민감한 환경변수는 누가, 어떻게 CI/CD 도구에 관리/주입할 것인가?

결정이 완료되면 선택하신 도구(GitLab 또는 Jenkins)에 맞춘 구체적인 설정 파일(`.gitlab-ci.yml` 또는 `Jenkinsfile`) 작성과 `deploy.py` 스크립트 리팩토링을 즉시 진행할 수 있습니다.
