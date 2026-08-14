# GitLab Server & Runner SSL/TLS 인증서 트러블슈팅 가이드

## 📌 개요 및 환경
* **GitLab Server**: Containerized GitLab (`https://10.226.50.6:10443`)
* **GitLab Runner**: Shell Executor (Docker 컨테이너 기반)
* **주요 이슈**: GitLab 서버 인증서 만료 및 SAN 미지정으로 인한 Runner 통신 불능, 파이프라인 내 `git clone` SSL 검증 실패

---

## 🚨 문제점 및 단계별 해결 로드맵

```
[이슈 1] 인증서 만료 (Expired)
   └── GitLab 서버에서 새 사설 인증서 재발급 및 Nginx 재시작
[이슈 2] Go/TLS SAN(Subject Alternative Name) 필드 누락
   └── -addext "subjectAltName=IP:10.226.50.6" 옵션으로 재발급
[이슈 3] Runner 컨테이너 내 파이프라인 git clone SSL 검증 실패
   └── OS 신뢰 인증서(Trust Store) 등록 (update-ca-certificates)
```

---

## 🛠️ 세부 문제 해결 과정

### 1. GitLab 서버 사설 인증서 재발급 (만료 및 SAN 누락 해결)

#### ❌ 발생 에러
1. `tls: failed to verify certificate: x509: certificate has expired or is not yet valid`
2. `tls: failed to verify certificate: x509: certificate relies on legacy Common Name field, use SANs instead`

#### 💡 원인
* 기존 사설 인증서의 유효기간 만료.
* Go 언어로 작성된 GitLab Runner가 최신 TLS 보안 표준에 따라 CN(Common Name)만 작성된 인증서를 거부하고 SAN(Subject Alternative Name)을 요구함.

#### ✅ 해결 방법 (GitLab 서버 컨테이너 내부 실행)
```bash
# 1. GitLab 서버 컨테이너 접속
docker exec -it <gitlab_container_id> bash

# 2. SSL 디렉터리 이동 및 기존 인증서 백업
cd /etc/gitlab/ssl
mv 10.226.50.6.crt 10.226.50.6.crt.bak
mv 10.226.50.6.key 10.226.50.6.key.bak

# 3. 유효기간(10년) 설정 및 SAN(Subject Alternative Name) 확장 필드가 포함된 인증서 발급
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout 10.226.50.6.key \
  -out 10.226.50.6.crt \
  -subj "/CN=10.226.50.6" \
  -addext "subjectAltName=IP:10.226.50.6"

# 4. 권한 변경 및 Nginx 재시작
chmod 600 10.226.50.6.key 10.226.50.6.crt
gitlab-ctl restart nginx
```

---

### 2. Runner 측 인증서 다운로드 명령어 구문 오류 수정

#### ❌ 발생 에러
1. `ash: openssl: command not found` (파이프 뒤 백슬래시 및 공백 문제)
2. `s_client: must not provide both -connect option and target parameter` (리다이렉션 기호 누락)

#### ✅ 해결 방법 (GitLab Runner 컨테이너 내부 실행)
`/dev/null` 앞에 입력 리다이렉션 기호(`<`)를 명확히 포함하여 한 줄로 실행:
```bash
openssl s_client -showcerts -connect 10.226.50.6:10443 </dev/null 2>/dev/null | openssl x509 -outform PEM > /etc/gitlab-runner/certs/10.226.50.6.crt
```

---

### 3. CI/CD 파이프라인 내 `git clone` SSL 검증 실패 해결

#### ❌ 발생 에러
```text
$ git clone https://aqa_team:****@10.226.50.6:10443/playwright/common.git
Cloning into 'common'...
fatal: unable to access 'https://10.226.50.6:10443/playwright/common.git/': server certificate verification failed. CAfile: none CRLfile: none
ERROR: Job failed: exit status 1
```

#### 💡 원인
GitLab Runner 데몬 자체는 `/etc/gitlab-runner/certs/` 안의 인증서를 인식하여 Job을 가져왔으나, Runner가 실행한 OS/System Git CLI가 해당 사설 인증서를 신뢰하지 못함.

#### ✅ 해결 방법 (Ubuntu/Debian 계열 Runner 컨테이너 내부 실행)
사설 인증서를 OS 전체가 신뢰하는 루트 인증서(Trust Store) 저장소로 등록:

```bash
# 1. 인증서를 OS 신뢰 인증서 경로로 복사
cp /etc/gitlab-runner/certs/10.226.50.6.crt /usr/local/share/ca-certificates/10.226.50.6.crt

# 2. OS 인증서 저장소 업데이트
update-ca-certificates

# 3. Runner 서비스 재시작
gitlab-runner restart
```

---

## 📝 최종 요약
1. **GitLab 서버**: 사설 인증서 갱신 시 유효기간 연장 및 SAN(`IP:10.226.50.6`) 확장 필드 추가.
2. **Runner 데몬**: `/etc/gitlab-runner/certs/10.226.50.6.crt`로 가져와 Runner <-> GitLab 통신 복구.
3. **OS System Git**: `update-ca-certificates` 명령어로 OS 전체 신뢰 저장소(Trust Store)에 등록하여 파이프라인 내 `git clone` 실패 복구.
