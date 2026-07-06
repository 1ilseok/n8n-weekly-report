✦ 현재 install.bat와 PM2를 통해 git-watcher가 백그라운드에서 주기적으로 코드를 Pull하고 앱을
  재시작하는 구조는, 특히 Windows 환경에서 PM2의 권한(UAC, Admin vs 일반 사용자 세션) 분리 문제와
  백그라운드 터미널 제어 문제로 인해 프로세스가 멈추거나 죽는(Stopped) 현상이 자주 발생할 수밖에
  없는 불안정한 아키텍처입니다.

  이러한 문제를 근본적으로 해결하기 위한 3가지 발전된 배포 및 구조 개선 방안을 제안합니다.

  ---

  제안 1. Native Windows Service 기반 단일화 및 셀프 업데이트 (가장 현실적인 개선)
  Node.js 생태계의 도구인 PM2(및 pm2-windows-startup)를 완전히 제거하고, Windows OS에 가장 친화적인
  네이티브 Windows 서비스 구조로 전환하는 방식입니다.

   * 구조 변경: PM2 대신 NSSM (Non-Sucking Service Manager) 또는 WinSW를 사용하여 에이전트 구동    
     파이썬 스크립트를 윈도우 서비스로 바로 등록합니다.
   * 작동 방식: git_watcher.py를 별도 프로세스로 분리하지 않고, 메인 애플리케이션(agent_daemon.py  
     또는 진입점) 내부에 '업데이트 체크 스레드'를 두거나, updater.exe(또는 py)라는 부모 서비스가   
     agent_daemon을 자식으로 띄우고 감시하는 구조(Watchdog)로 변경합니다. Git 변경사항이 발견되면  
     부모 서비스가 자식을 종료시키고, git pull을 수행한 후 자식을 다시 실행합니다.
   * 장점:
       * PM2 for Windows 특유의 고질적인 권한 및 세션 분리 문제(관리자 권한 충돌)가 완전히
         해결됩니다.
       * Windows 부팅 시 백그라운드에서 가장 안정적이고 확실하게 실행이 보장됩니다.
       * 대상 PC에 Node.js나 PM2 글로벌 패키지를 설치할 필요가 없어집니다.

  제안 2. Git Polling 폐기 및 Push 기반 CI/CD 파이프라인 도입 (GitLab Runner / Webhook)
  클라이언트 PC가 5분마다 무한히 git fetch를 호출하는 비효율적인 Polling 구조를 버리고, 이벤트가
  발생할 때만 서버가 클라이언트에 명령을 내리는 Push 기반 구조입니다.

   * 구조 변경: 주기적으로 확인하는 git-watcher 스크립트를 아예 삭제합니다. 대신 대상(Endpoint)
     PC에 GitLab Runner(Shell 모드)를 설치하거나, 아주 가벼운 Webhook 수신기를 띄워둡니다.
   * 작동 방식:
      개발자가 master 브랜치에 코드를 Push하거나 Merge하면, GitLab CI/CD가 트리거되어 타겟 대상
  PC에 설치된 Runner를 통해 배포 파이프라인(Job)을 직접 실행합니다. 해당 Job 안에서 git pull 및
  프로세스 재시작(pm2 restart 또는 서비스 재시작) 스크립트를 수행합니다.
   * 장점:
       * 불필요한 백그라운드 Git 트래픽과 리소스 낭비, 파일 잠금(Lock) 문제가 발생하지 않습니다.
       * 업데이트 성공/실패 여부를 대상 PC의 로컬 로그를 뒤질 필요 없이, GitLab 웹 화면에서
         중앙집중적으로 파악할 수 있습니다.

  제안 3. 소스코드 배포 중단 및 바이너리(EXE) 패키징 + OTA(Over-The-Air) 업데이트
  현재처럼 대상 PC에 소스코드를 전부 내려받고, 현장에서 pip install과 npm build를 수행하는
  방식(의존성 꼬임의 주범)을 버리고, 현대적인 데스크톱 앱 배포 방식을 채택합니다.

   * 구조 변경: 타겟 PC에서 Git, Python venv, Node.js, PM2에 의존하는 구조를 모두 없앱니다. 개발
     서버(CI)에서 파이썬 코드와 프론트엔드 정적 파일을 PyInstaller나 Nuitka를 사용해 하나의 실행
     파일(Agent.exe)로 컴파일하여 배포합니다.
   * 작동 방식:
      Agent.exe가 실행될 때, 자체적으로 버전 정보 파일(예: AWS S3, GitLab Raw 파일, 혹은 내부
  서버의 version.json)을 읽어옵니다. 새로운 버전이 있다면 Updater.exe를 임시로 실행하여 새 버전의
  압축 파일을 다운로드하여 기존 Agent.exe를 덮어쓰고 재시작합니다 (Discord, Slack 앱 등의 업데이트
  방식).
   * 장점:
       * 엔드포인트(대상 PC) 환경이 어떠하든(설치된 파이썬/노드 버전이 달라도) "환경이 꼬여서
         설치/실행에 실패하는 일"이 0에 수렴합니다.
       * 설치 속도가 수초 내로 극단적으로 짧아지며, 보안상 소스 코드가 외부에 직접 노출되지
         않습니다.

  ---

  추천 요약:
   * 당장 인프라 변경 없이 가장 빠르게 안정성을 확보하려면 [제안 1] NSSM을 통한 Windows Service화 +                                 
     자체 Watchdog 구조로 개편하시는 것을 가장 권장합니다.
   * 향후 대량의 에이전트 PC를 관리해야 한다면 최종적으로는 [제안 3] 바이너리 패키징 및 OTA
     업데이트 방식으로 가시는 것이 유지보수 비용을 가장 크게 아낄 수 있습니다.