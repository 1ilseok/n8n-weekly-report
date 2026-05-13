

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

# Jenkins

## "곧 Jenkins가 종료될 예정입니다" 배너가 나타날 경우
- http://<Jenkins주소>/cancelQuietDown 접속
- "Retry using POST" 버튼을 클릭하여 취소
- ThinBackup이 완료되지 못하고 있는 것과 관련이 있음.
- **위와 같이 해봤지만, 다시 배너가 나타남. 결국 jenkins restart가 답.