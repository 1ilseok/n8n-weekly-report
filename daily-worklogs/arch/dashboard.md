
---

# Elasticsearch

## Elasticsearch 기동 실패 - write.lock 문제 해결 메모

**환경:** Elasticsearch 5.6.17 / 데이터 경로 `/somansa/data/es_data`

### 증상

ES 서비스 기동 시 9200 포트 미응답, 아래 두 가지 에러 로그 발생.

**① 노드 기동 단계 실패**
```
IllegalStateException: failed to obtain node locks,
tried [[/somansa/data/es_data/SMS_LogServer]] with lock id [0]
```

**② 샤드 복구 단계 실패**
```
LockObtainFailedException: Lock held by another program:
/somansa/data/es_data/nodes/0/indices/{uuid}/{shard}/index/write.lock
```

### 원인

ES가 비정상 종료되면서 Lucene이 생성한 `write.lock` 파일이 삭제되지 않고 잔존. 재기동 시 해당 lock을 획득하지 못해 샤드 복구 전체 실패.

### 해결 절차
```bash
# 1. ES 완전 종료
systemctl stop elasticsearch

# 2. 잔존 프로세스 확인
ps -ef | grep elasticsearch | grep -v grep

# 3. write.lock 일괄 삭제
find /somansa/data/es_data/nodes/0/indices -name "write.lock" -exec rm -f {} \;

# 4. ES 재시작 및 로그 확인
systemctl start elasticsearch
journalctl -u elasticsearch -f
```

### 주의사항

- `write.lock`은 OS 레벨 Native Lock이므로, **ES 프로세스를 완전히 종료한 후** 삭제해야 함
- 프로세스가 살아있는 상태에서 lock 파일만 삭제해도 락은 해제되지 않음
- 재발 방지를 위해 ES는 항상 `systemctl stop`으로 정상 종료할 것

---
# /somansa/data/es_log/가 사이즈가 클때
- node.lock 삭제
  - ES 완전 종료 상태에서 해야함.
  - rm -f /somansa/data/es_data/nodes/0/node.lock
  - 로그파일 일괄 삭제하고 재기동 후 확인.

---

# Jenkins

## "곧 Jenkins가 종료될 예정입니다" 배너가 나타날 경우
- http://<Jenkins주소>/cancelQuietDown 접속
- "Retry using POST" 버튼을 클릭하여 취소
- ThinBackup이 완료되지 못하고 있는 것과 관련이 있음.
- **위와 같이 해봤지만, 다시 배너가 나타남. 결국 jenkins restart가 답.


# Webkeeper
## WKServer 동작 실패
- 조치 방법
1. cm이나 명령어로 WKServer 동작 제어가 안된다면
2. /somansa/cm/conf/database.info의 Password 항목과 /somansa/webkeeper/conf/WKConfigReg.xml 의 두 패스워드가 일치하는지 확인하고, 일치하지 않는다면 /somansa/cm/conf/database.info의 Password 항목으로 /somansa/webkeeper/conf/WKConfigReg.xml 의 두 패스워드를 맞춰 줘야한다.
3. /somansa/webkeeper/conf/WKConfigReg.xml NetworkAgent와 DBMS의 DBHost를 127.0.0.1로 넣어준다.
4. 그 후, /somansa/webkeeper/log/WKServer.log를 보면서 cm이나 명령어로 WKServer 동작한다.
5. 로그 상에 /somansa/webkeeper/db_update/에 BlkPorts10.db3 가 없다는 로그가 있으면 넣어준다. (/somansa/webkeeper/db/에 파일이 있으면 /somansa/webkeeper/db_update/dp에 없어도 되는거 같기도 하다. 확실하지는 않음.)
6. DB 업데이트 페이지에서 업데이트를 진행해보고 잘 되는지 확인한다.
7. 그냥 아래와 같이 맞춰주면 됨.

[/somansa/webkeeper/conf/WKConfigReg.xml]
<?xml version="1.0" encoding="UTF-8"?>
<WebKeeperConfig>
<Root>
        <PkgType>0</PkgType>
        <Language>kor</Language>
        <ShaMode>512</ShaMode>
        <UpdateDebug>off</UpdateDebug>
</Root>
<NetworkAgent>
        <DBHost>127.0.0.1</DBHost>
        <DBPort>5432</DBPort>
        <Login>fdc58398943393b926883ef59d9e4c39</Login>
        <Passwd>87bb677bc7f90dba1690dc0b6bffa62a</Passwd>
</NetworkAgent>
<DBMS>
        <DBHost>127.0.0.1</DBHost>
        <DBPort>5432</DBPort>
        <Login>fdc58398943393b926883ef59d9e4c39</Login>
        <Passwd>87bb677bc7f90dba1690dc0b6bffa62a</Passwd>
        <ClientTLS>true</ClientTLS>
        <DbmsTLS>false</DbmsTLS>
</DBMS>
</WebKeeperConfig>

# 프로토콜 현황조사용 계정 정보 (웹메일, 메신저 등)
- https://docs.google.com/spreadsheets/d/1XjzCca5fuZqntE_GE_y5xzV7QRJ9RaBKONceijfRBIc/edit?pli=1&gid=600839848