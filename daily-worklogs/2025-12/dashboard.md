- 추후 : briefit에 대기업 기술블로그 (토스, 우아한형제 등) 추가

- DB 복원실패현상 팀장님 문의 (Maili에서 최초 발견)
- AI 기반 스크립트 유지보수 자동화
    - 차주에 원용씨가 모든 프로토콜 job에 대해서, 한번이라도 성공 시키면 그 이후로 모니터링해서 유지보수 기능 확인해보는 것으로.
- macos 유지보수 계획
    - airdrop 제외
    - usbctl 적용
        
        ```jsx
        # 1. 홈브루를 통해 설치
        brew install uhubctl
        
        # 2. 연결된 허브 정보 출력 (지원 여부 확인)
        sudo uhubctl
        
        # 3. 출력 결과
        aqa@AQAM1iMac ~ % sudo uhubctl
        Password:
        
        Current status for hub 0-2 [050d:092c Belkin International Belkin USB-C Multimedia Hub 000000000, USB 3.20, 4 ports, ppps]
        
          Port 1: 02a0 power 5gbps Rx.Detect
        
          Port 2: 02a0 power 5gbps Rx.Detect
        
          Port 3: 02a0 power 5gbps Rx.Detect
        
          Port 4: 0203 power 5gbps U0 enable connect [0bda:8153 Realtek USB 10/100/1000 LAN 001000001]
        
        Current status for hub 0-1 [050d:092b Belkin International Belkin USB-C Multimedia Hub 000000000, USB 2.10, 4 ports, ppps]
        
          Port 1: 0100 power
        
          Port 2: 0503 power highspeed enable connect [05ac:12a8 Apple Inc. iPhone 0000811000145C9401A2401E]
        
          Port 3: 0503 power highspeed enable connect [13fd:0840 Generic External 534243343730383336312020]
        
          Port 4: 0503 power highspeed enable connect [1a40:0101 USB 2.0 Hub, USB 2.00, 4 ports, ganged]
        
        Current status for hub 1-1 [050d:090b CE-Link USB-C HUB, USB 2.10, 4 ports, ppps]
        
          Port 1: 0100 power
        
          Port 2: 0100 power
        
          Port 3: 0100 power
        
          Port 4: 0103 power enable connect [046d:c534 Logitech USB Receiver]
        
        Current status for hub 1-2 [050d:090c CE-Link USB-C HUB, USB 3.00, 4 ports, ppps]
        
          Port 1: 02a0 power 5gbps Rx.Detect
        
          Port 2: 02a0 power 5gbps Rx.Detect
        
          Port 3: 0203 power 5gbps U0 enable connect [0781:5567  USB  SanDisk 3.2Gen1 0901c0efaeb0d0509fae40b909f575123321be1d23412ae9e977c6131fa5d1b]
        
          Port 4: 02a0 power 5gbps Rx.Detect
        ```
        
        ```jsx
        # iPhone 재부팅
        sudo uhubctl -l 0-1 -p 2 -a cycle
        
        # SanDisk USB 메모리 재부팅
        sudo uhubctl -l 1-2 -p 3 -a cycle
        ```
        
    - playwright 전환

읽어보기

https://toss.tech/article/ai-driven-ui-test-automation

briefit - 대기업 기술블로그 (토스, 우아한형제 등) 추가

---

---

- macos는 사이트별로 사용하지 않을 기능 xml 파일 보고 tc 스킵하도록
- wk 기능리스트 관련, 비즈니스 로직은 1팀 QA 담당에게 문의
- playwright bdd 자동화 실월간 발표자료 작성.
    - allure report 보여주고, bdd가 어떤건지도 보여주고, Gherkin 문법적인 내용도 포함되면 좋을 것.
    - BDD란? 기획자가 시나리오를 작성하고, QA가 필터링하고 이거를 개발자가 그대로 개발.
- 연말에 glusterfs 관련 somansa-shell 수정 (glusterfs 관련 소유권 확인해보기) (`sudo gluster peer probe var_1`)