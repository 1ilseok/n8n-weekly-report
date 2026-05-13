# 사내망 Jenkins 플러그인 설치를 위한 SSH 터널링 설정 가이드

## 환경 정보

| 항목 | 내용 |
|------|------|
| Jenkins 호스트 | qa-package (사내망, 외부 인터넷 차단) |
| Jenkins 실행 방식 | Docker Compose 컨테이너 |
| Docker 네트워크 | jenkins_default (gateway: 172.18.0.1) |
| 점프 서버 | 외부망 접근 가능한 중간 서버 |
| 목적 | updates.jenkins.io 접근하여 플러그인 설치 |

## 전체 구조

```
[Jenkins 컨테이너 172.18.0.2]
        ↓ HTTP 프록시 (172.18.0.1:8118, privoxy)
        ↓ SOCKS5 동적 프록시 (172.18.0.1:1080)
[호스트 qa-package]
        ↓ SSH 터널 (autossh + systemd)
[점프 서버 (외부망 접근 가능)]
        ↓
[updates.jenkins.io → mirrors → cloudflare CDN]
```

## 왜 이 구조인가? (삽질 히스토리)

처음에는 단순하게 SSH 포트포워딩(`-L`)만 쓰려 했으나 아래 문제들이 연쇄적으로 발생했다.

**문제 1: 정적 포트포워딩의 한계**
updates.jenkins.io가 단순히 하나의 IP로 연결되지 않는다.
`updates.jenkins.io → mirrors.updates.jenkins.io → westeurope/eastamerica.cloudflare.jenkins.io`
도메인마다 IP가 달라서 `-L` 방식으로는 모든 경로를 커버할 수 없다.
→ **SOCKS5 동적 프록시(`-D`)로 전환**

**문제 2: Java 신규 HTTP 클라이언트의 SOCKS5 무시**
Jenkins가 사용하는 Java 11+ `java.net.http.HttpClient`는 JVM의 `-DsocksProxyHost` 옵션을 무시한다.
→ **privoxy(HTTP→SOCKS5 브릿지) 추가**

**문제 3: SSL 인증서 신뢰 문제**
점프 서버 네트워크에서 Somansa DPI(SSL 패킷 검사)를 하므로 인증서 체인이 바뀐다.
터널을 통하면 Let's Encrypt 인증서가 직접 오는데, Jenkins JVM의 cacerts에 중간 CA(R13)가 없다.
→ **Let's Encrypt R13 중간 CA를 Java cacerts에 등록**

**문제 4: qa-package 호스트의 DNS 오염**
qa-package에서 `updates.jenkins.io`가 `::` (IPv6 null)로 잘못 해석된다.
autossh 터널의 목적지 DNS를 호스트가 결정하므로 K8s 내부로 빠진다.
→ **터널 목적지를 실제 IP(128.24.70.119)로 하드코딩**

---

## 0단계. 사전 확인

```bash
# Docker 네트워크 gateway IP 확인 (환경마다 다를 수 있음)
docker network inspect jenkins_default | grep Gateway
# → 172.18.0.1 확인

# autossh 설치 여부 확인
which autossh

# 포트 충돌 확인
ss -tlnp | grep -E '1080|8118'
```

---

## 1단계. autossh 설치

```bash
# RHEL/CentOS/Rocky
sudo yum install -y autossh

# Ubuntu/Debian
sudo apt install -y autossh

autossh -V
```

---

## 2단계. 터널 전용 계정 및 SSH 키 생성

Jenkins는 컨테이너 안에서만 동작하므로 호스트에 jenkins 계정이 없다.
autossh 전용 계정을 별도로 만든다.

```bash
# 호스트 전용 계정 생성 (로그인 불가 시스템 계정)
sudo useradd -r -m -s /bin/false tunnel-user

# SSH 키 생성 (passphrase 반드시 빈칸)
sudo mkdir -p /home/tunnel-user/.ssh
sudo chmod 700 /home/tunnel-user/.ssh
sudo -u tunnel-user ssh-keygen -t ed25519 \
  -f /home/tunnel-user/.ssh/jenkins_tunnel_key \
  -C "jenkins-tunnel" \
  -N ""

# 점프 서버에 공개키 등록
sudo -u tunnel-user ssh-copy-id \
  -i /home/tunnel-user/.ssh/jenkins_tunnel_key.pub \
  유저명@점프서버_IP

# 접속 테스트 (비밀번호 묻지 않고 "연결 성공" 출력되면 정상)
sudo -u tunnel-user ssh \
  -i /home/tunnel-user/.ssh/jenkins_tunnel_key \
  -o BatchMode=yes \
  유저명@점프서버_IP \
  echo "연결 성공"
```

---

## 3단계. updates.jenkins.io 실제 IP 확인

**점프 서버에서 실행:**

```bash
curl -v https://updates.jenkins.io/current/update-center.json 2>&1 | grep "Trying"
# → Trying 128.24.70.119...
```

이 IP를 다음 단계에서 하드코딩한다.
(qa-package 호스트의 DNS가 오염되어 있어 도메인 이름을 쓰면 안 됨)

---

## 4단계. Systemd 서비스 파일 생성 (SOCKS5 동적 프록시)

```bash
sudo vi /etc/systemd/system/jenkins-tunnel.service
```

```ini
[Unit]
Description=Jenkins Update Center SSH Tunnel
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=tunnel-user
Environment=AUTOSSH_GATETIME=0

ExecStart=/usr/bin/autossh -M 0 -N \
  -o "ServerAliveInterval 60" \
  -o "ServerAliveCountMax 3" \
  -o "StrictHostKeyChecking=no" \
  -o "ExitOnForwardFailure=yes" \
  -i /home/tunnel-user/.ssh/jenkins_tunnel_key \
  -D 172.18.0.1:1080 \
  유저명@점프서버_IP

Restart=on-failure
RestartSec=30
SyslogIdentifier=jenkins-tunnel

[Install]
WantedBy=multi-user.target
```

> **핵심 포인트**
> - `-D 172.18.0.1:1080` : SOCKS5 동적 프록시. 도메인/IP에 상관없이 모든 연결을 터널로 보냄
> - 정적 포트포워딩(`-L`) 대신 동적 프록시를 쓰는 이유: updates.jenkins.io가 여러 CDN 도메인으로 redirect되기 때문

```bash
sudo systemctl daemon-reload
sudo systemctl enable jenkins-tunnel
sudo systemctl start jenkins-tunnel

# 확인 (Active: active (running) 이어야 정상)
sudo systemctl status jenkins-tunnel
ss -tlnp | grep 1080
```

---

## 5단계. privoxy 설치 및 설정 (HTTP → SOCKS5 브릿지)

Java 신규 HTTP 클라이언트는 SOCKS5 JVM 옵션을 무시한다.
HTTP 프록시 설정은 인식하므로 privoxy로 브릿지한다.

```bash
# RHEL/CentOS/Rocky
sudo yum install -y privoxy

# Ubuntu/Debian
sudo apt install -y privoxy
```

```bash
sudo vi /etc/privoxy/config
```

기존 `listen-address` 라인 주석 처리 후 아래 내용 추가:

```
# 기존 라인 주석 처리
# listen-address  127.0.0.1:8118

# Docker gateway에서 수신
listen-address  172.18.0.1:8118

# SOCKS5 터널로 upstream 연결
forward-socks5 / 172.18.0.1:1080 .
```

```bash
# 기존 listen-address 자동 주석 처리
sudo sed -i 's/^listen-address  127.0.0.1:8118/# listen-address  127.0.0.1:8118/' /etc/privoxy/config

sudo systemctl enable privoxy
sudo systemctl start privoxy

# 포트 확인
ss -tlnp | grep 8118
# 172.18.0.1:8118 이 LISTEN 이어야 정상
```

---

## 6단계. Let's Encrypt R13 중간 CA 인증서 등록

SSH 터널을 통하면 Somansa DPI를 우회하므로 실제 Let's Encrypt 인증서가 온다.
Jenkins JVM의 cacerts에 R13 중간 CA가 없으면 SSLHandshakeException이 발생한다.

```bash
# 중간 CA 인증서 추출
openssl s_client \
  -connect updates.jenkins.io:443 \
  -proxy 172.18.0.1:8118 \
  -servername updates.jenkins.io \
  -showcerts 2>/dev/null \
  | awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/' \
  | awk 'BEGIN{n=0} /BEGIN CERTIFICATE/{n++} n==2{print}' \
  > /tmp/letsencrypt-r13.crt

# 내용 확인 (-----BEGIN CERTIFICATE----- 로 시작하면 정상)
cat /tmp/letsencrypt-r13.crt

# 컨테이너에 복사 및 Java truststore에 등록
docker cp /tmp/letsencrypt-r13.crt jenkins:/tmp/letsencrypt-r13.crt

docker exec -u root jenkins \
  keytool -import -trustcacerts \
  -alias letsencrypt-r13 \
  -file /tmp/letsencrypt-r13.crt \
  -keystore /opt/java/openjdk/lib/security/cacerts \
  -storepass changeit \
  -noprompt

# 등록 확인
docker exec jenkins \
  keytool -list \
  -keystore /opt/java/openjdk/lib/security/cacerts \
  -storepass changeit \
  -alias letsencrypt-r13
```

> ⚠️ **주의**: `docker compose down && up`으로 컨테이너를 재생성하면 인증서 등록이 사라진다.
> 영구 적용은 아래 7단계 참고.

---

## 7단계. docker-compose.yml 설정

```yaml
services:
  jenkins:
    image: jenkins/jenkins:lts-jdk21
    container_name: jenkins
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - /var/lib/docker/volumes/jenkins_home/_data:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - TZ=Asia/Seoul
      # 모든 JAVA_OPTS는 반드시 한 줄로 합쳐야 함 (중복 키는 마지막 값만 적용됨)
      - JAVA_OPTS=-Dhudson.model.DirectoryBrowserSupport.CSP= -Dfile.encoding=UTF-8 -Dhttps.proxyHost=172.18.0.1 -Dhttps.proxyPort=8118 -Dhttp.proxyHost=172.18.0.1 -Dhttp.proxyPort=8118 -Dhttp.nonProxyHosts=localhost|127.0.0.1
      - JENKINS_JAVA_OPTIONS=-Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8 -Dhudson.util.ProcessTree.disable=true
    user: "1000:1000"
    logging:
      driver: "journald"
```

> ⚠️ **JAVA_OPTS 중복 주의**: 같은 키를 두 줄에 걸쳐 쓰면 마지막 값만 적용된다.
> 반드시 한 줄로 모든 옵션을 합쳐야 한다.

```bash
docker compose down && docker compose up -d

# JAVA_OPTS 확인 (한 줄에 모든 옵션이 보여야 정상)
docker exec jenkins env | grep JAVA_OPTS
```

---

## 8단계. 컨테이너 재생성 후 인증서 재등록

컨테이너를 재생성할 때마다 6단계의 인증서 등록을 반복해야 한다.

```bash
docker cp /tmp/letsencrypt-r13.crt jenkins:/tmp/letsencrypt-r13.crt

docker exec -u root jenkins \
  keytool -import -trustcacerts \
  -alias letsencrypt-r13 \
  -file /tmp/letsencrypt-r13.crt \
  -keystore /opt/java/openjdk/lib/security/cacerts \
  -storepass changeit \
  -noprompt

docker compose restart
```

---

## 9단계. Jenkins Update Site URL 설정

```
Jenkins 관리 → Plugins → Advanced settings → Update Site URL

https://updates.jenkins.io/update-center.json
```

→ **Check Now** 클릭 → 플러그인 목록 갱신 확인

---

## 최종 동작 확인 명령어

```bash
# 1. SOCKS5 터널 확인
ss -tlnp | grep 1080

# 2. privoxy 확인
ss -tlnp | grep 8118

# 3. 컨테이너에서 HTTP 프록시 경유 테스트
docker exec jenkins curl -v \
  --proxy http://172.18.0.1:8118 \
  https://updates.jenkins.io/current/update-center.json 2>&1 \
  | grep -E "Trying|subject|HTTP"
# 기대 결과:
# Trying 172.18.0.1:8118...
# subject: CN=updates.jenkins.io
# HTTP/2 307 (또는 200)
```

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| autossh 서비스 시작 실패 | SSH 키 권한 문제 | `chmod 600 /home/tunnel-user/.ssh/jenkins_tunnel_key` |
| SOCKS5 포트 안 열림 | 점프 서버 접속 실패 | 키 등록 및 접속 테스트 재확인 |
| SSLHandshakeException | 인증서 미등록 | 6단계 인증서 등록 반복 |
| HTTP connect timed out | Java 신규 HTTP 클라이언트가 SOCKS5 무시 | privoxy 경유 HTTP 프록시 설정 확인 |
| JAVA_OPTS 일부 옵션 미적용 | 중복 키 문제 | 모든 옵션을 한 줄로 합치기 |
| 터널이 엉뚱한 곳으로 연결 | 호스트 DNS 오염 | 서비스 파일에서 도메인 대신 실IP 사용 |

```bash
# 서비스 로그 확인
sudo journalctl -u jenkins-tunnel -f

# privoxy 로그 확인
sudo journalctl -u privoxy -f
```

---

## 영구 인증서 적용 (선택사항)

컨테이너 재생성 시 자동으로 인증서가 적용되게 하려면 Dockerfile로 커스텀 이미지를 빌드한다.

```dockerfile
FROM jenkins/jenkins:lts-jdk21
USER root
COPY letsencrypt-r13.crt /tmp/letsencrypt-r13.crt
RUN keytool -import -trustcacerts \
    -alias letsencrypt-r13 \
    -file /tmp/letsencrypt-r13.crt \
    -keystore /opt/java/openjdk/lib/security/cacerts \
    -storepass changeit \
    -noprompt
USER jenkins
```

```bash
# 이미지 빌드
docker build -t jenkins-custom:lts-jdk21 .

# docker-compose.yml에서 image 변경
# image: jenkins-custom:lts-jdk21
```
