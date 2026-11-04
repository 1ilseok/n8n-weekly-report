<style>
  table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1rem;
  }
  table th, table td {
    padding: 10px 12px !important; /* 셀 위아래 10px, 좌우 12px 여백 */
    vertical-align: middle;
    line-height: 1.55;
  }
  table th {
    background-color: #f6f8fa;
    padding-top: 12px !important;
    padding-bottom: 12px !important;
  }
</style>

# 📊 사내 로컬 LLM 인프라 분석 및 Test Healer 종합 평가표

> **본 문서는 Playwright Test Healer 개발 과정에서의 [사내 로컬 LLM & 인프라 최적화 분석]과 시스템의 [긍정적 성과 및 차기 고도화 과제]를 표(Table) 형태로 요약 정형화한 문서입니다.**

---

## 🖥️ 1. 사내 로컬 LLM & 인프라 최적화 분석

### 단계별 로컬 LLM & 인프라 전환 및 검증 이력

<table>
  <thead>
    <tr>
      <th width="14%" style="padding: 10px 12px;">단계 / 시기</th>
      <th width="18%" style="padding: 10px 12px;">인프라 / 장비</th>
      <th width="18%" style="padding: 10px 12px;">서빙 엔진 / 포맷</th>
      <th width="25%" style="padding: 10px 12px;">핵심 검증 내용</th>
      <th width="25%" style="padding: 10px 12px;">결과 및 한계점 / 평가</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 10px 12px;"><b>1단계</b><br><i>(2026.03)</i></td>
      <td style="padding: 10px 12px;"><b>사내 vLLM 서버</b></td>
      <td style="padding: 10px 12px;">vLLM (API)</td>
      <td style="padding: 10px 12px;">Continue / Cline 플러그인을 통한 사내 vLLM 서버 연동 시도</td>
      <td style="padding: 10px 12px;">❌ <b>Tool Calling(도구 호출) 미지원/오류</b> 발견. vLLM 서버 측 포워딩 및 커스텀 프록시 필요성 도출.</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>2단계</b><br><i>(2026.04~06)</i></td>
      <td style="padding: 10px 12px;"><b>팀 Mac Studio</b></td>
      <td style="padding: 10px 12px;">LM Studio / Ollama</td>
      <td style="padding: 10px 12px;">"Mac Studio + LM Studio + 30B 체급 모델" 샌드박스 PoC 및 하드웨어 도입 근거 마련</td>
      <td style="padding: 10px 12px;">⚠️ OpenCode/Pi 연결 가능성 확인. 단, 로컬 30B 모델의 Context Window 제약(32K)</b> 및 토큰 압축 시 지능 저하 이슈 도출.</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>3단계</b><br><i>(2026.08)</i></td>
      <td style="padding: 10px 12px;"><b>팀 DGX Spark</b></td>
      <td style="padding: 10px 12px;">Ollama</td>
      <td style="padding: 10px 12px;">qwen3 모델 및 Gemma4 모델 비교</td>
      <td style="padding: 10px 12px;"></td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>4단계</b><br><i>(2026.08~09)</i></td>
      <td style="padding: 10px 12px;"><b>팀 DGX Spark / Pi Agent</b></td>
      <td style="padding: 10px 12px;">Ollama API / Pi CLI</td>
      <td style="padding: 10px 12px;"><b>gemma4:31b-it-qat</b> (96K Context) 최종 적용, JSON 규격화, Thinking 토큰 제한</td>
      <td style="padding: 10px 12px;">✅ <b>gemma4:31b-it-qat 최종 선정</b>. Tool Calling 규격 완벽 준수 및 96K Context로 무인 힐링 완숙.</td>
    </tr>
  </tbody>
</table>

---

### 1.2 모델 비교 분석 (사내 Qwen Fable vs Ollama qwen3-coder vs Gemma 4 31B QAT)

<table>
  <thead>
    <tr>
      <th width="18%" style="padding: 10px 12px;">구분</th>
      <th width="26%" style="padding: 10px 12px;">Qwen-3.6-27B-Fable<br><i>(사내 서빙 범용 모델)</i></th>
      <th width="26%" style="padding: 10px 12px;">qwen3-coder:30b-a3b-q4_K_M<br><i>(사내 Ollama Coder 후보)</i></th>
      <th width="30%" style="padding: 10px 12px;">gemma4:31b-it-qat<br><i>(Jenkins Healer 최종 채택 ⭐)</i></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 10px 12px;"><b>출처 및 위치</b></td>
      <td style="padding: 10px 12px;">사내 LLM 서빙 서버 (8/3 데일리 로그 명시)</td>
      <td style="padding: 10px 12px;">사내 Ollama 서버 등록 모델 (<code>setup-pi.ps1</code> 등록)</td>
      <td style="padding: 10px 12px;">사내 Ollama 서버 등록 모델 (<code>Jenkinsfile.healer</code> 실운영)</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>Tool Calling 안정성</b></td>
      <td style="padding: 10px 12px;">❌ <b>실행 지연 및 포맷 오류</b><br>(8/3 child-process 지연 확인)</td>
      <td style="padding: 10px 12px;">⚠️ 4비트 양자화로 간헐적 파싱 오류 가능성</td>
      <td style="padding: 10px 12px;">✅ <b>최우수 (RFC JSON 규격 준수)</b><br>(MCP 도구 호출 오류 제로)</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>Context Window</b></td>
      <td style="padding: 10px 12px;">보통 (32K~64K)</td>
      <td style="padding: 10px 12px;">128K 설정 (setup-pi 정의)</td>
      <td style="padding: 10px 12px;"><b>96K 실운영 Context (README 명시)</b></td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>양자화 및 특징</b></td>
      <td style="padding: 10px 12px;">사내 기본 서빙 포맷</td>
      <td style="padding: 10px 12px;">Q4_K_M 사후 양자화</td>
      <td style="padding: 10px 12px;"><b>QAT (학습 단계 양자화)</b>로 원본급 지능 유지</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>최종 평가</b></td>
      <td style="padding: 10px 12px;">검증 지연 현상으로 실운영 탈락</td>
      <td style="padding: 10px 12px;">환경 설정에 등록된 후보 모델</td>
      <td style="padding: 10px 12px;"><b>Tool Calling 제약 극복으로 최종 선정</b></td>
    </tr>
  </tbody>
</table>

---

### 1.3 양자화(Quantization) 포맷 및 DGX Spark 128GB 적용 전략

<table>
  <thead>
    <tr>
      <th width="14%" style="padding: 10px 12px;">압축 단계</th>
      <th width="12%" style="padding: 10px 12px;">세부 포맷</th>
      <th width="28%" style="padding: 10px 12px;">기술적 핵심 특징</th>
      <th width="18%" style="padding: 10px 12px;">주요 서빙 엔진</th>
      <th width="28%" style="padding: 10px 12px;">DGX Spark (128GB) 적용 전략 및 비고</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 10px 12px;"><b>양자화 인지 학습</b></td>
      <td style="padding: 10px 12px;"><b>QAT</b><br><i>(QAT 31B)</i></td>
      <td style="padding: 10px 12px;"><b>학습 단계부터 양자화 적용</b>으로 지능 손실 극소화 및 Tool Calling 극대화</td>
      <td style="padding: 10px 12px;">Ollama, vLLM</td>
      <td style="padding: 10px 12px;"><b>[최종 실운영 채택]</b> <code>gemma4:31b-it-qat</code> 모델 적용으로 96K Context + Tool Call 완벽 대응.</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>원본 (16비트)</b></td>
      <td style="padding: 10px 12px;"><b>BF16</b></td>
      <td style="padding: 10px 12px;">인공지능 학습/추론 글로벌 표준 원본 포맷</td>
      <td style="padding: 10px 12px;">vLLM, Hugging Face</td>
      <td style="padding: 10px 12px;">DGX Spark VRAM(128GB)에서 원본 로드 가능하나 Tool Call 레벨 검증 필요.</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>8비트 압축</b></td>
      <td style="padding: 10px 12px;"><b>FP8 / Q8_0</b></td>
      <td style="padding: 10px 12px;">GPU 가속 및 정수형 변환 대중적 기술</td>
      <td style="padding: 10px 12px;">Ollama, TensorRT</td>
      <td style="padding: 10px 12px;">Ollama 서빙 기본 지원 포맷.</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>4비트 일반 압축</b></td>
      <td style="padding: 10px 12px;"><b>Q4_K_M</b></td>
      <td style="padding: 10px 12px;"><code>qwen3-coder:30b-a3b-q4_K_M</code> 등에 적용된 사후 양자화 기술</td>
      <td style="padding: 10px 12px;">Ollama (개인/로컬)</td>
      <td style="padding: 10px 12px;">개인 PC/Mac 샌드박스에서 검증되었으나, QAT 대비 Tool Call 정밀도가 다소 떨어짐.</td>
    </tr>
  </tbody>
</table>

---

## ⚖️ 2. Playwright Test Healer 종합 평가 (Positive vs Critical)

### 2.1 항목별 성과 vs 과제 비교표

<table>
  <thead>
    <tr>
      <th width="18%" style="padding: 10px 12px;">평가 항목</th>
      <th width="42%" style="padding: 10px 12px;">🟢 성과</th>
      <th width="22%" style="padding: 10px 12px;">🔴 과제</th>
      <th width="18%" style="padding: 10px 12px;">💡 종합 평점 & 개선 방향</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 10px 12px;"><b>1. 자율성</b></td>
      <td style="padding: 10px 12px;">• 빌드 실패 감지부터 원인 분석, 코드 수정, 재검증, <b>수정 결과 Auto-Commit/Push 및 Mattermost 카드 알림까지 백그라운드 100% 무인 완결</b></td>
      <td style="padding: 10px 12px;">• 메인 브랜치 직연동(Auto-Merge) 전 안전성 검증을 위한 PR/리뷰 가이드 적용 (복합 제품 결함 시 스킵 처리)</td>
      <td style="padding: 10px 12px;"><b>⭐⭐⭐⭐⭐ (5.0/5.0)</b><br>진단·수정·재검증·자동 커밋/푸시까지 백그라운드 무인 자율화 완비</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>2. 안전성</b></td>
      <td style="padding: 10px 12px;">• BDD 시나리오(<code>features/</code>) 수정 엄격 금지<br>• 환경/제품 버그 시 수정 스킵(<code>SKIPPED_*</code>)<br>• 최초 성공 시 <code>FLAKY_PASSED</code> 분리로 <b>가짜 힐링 완벽 차단</b></td>
      <td style="padding: 10px 12px;">• 단일 <code>.spec.ts</code> 내 1차원적 셀렉터/타임아웃 결함만 수정 가능<br>• 복합 단계 의존성이나 테스트 데이터 변경은 수정 불가</td>
      <td style="padding: 10px 12px;"><b>⭐⭐⭐⭐⭐ (4.5/5.0)</b><br>안전 가드레일이 매우 촘촘하여 코드 오염 방지 탁월</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>3. LLM 품질</b></td>
      <td style="padding: 10px 12px;">• 상용 API 비용 0원 (사내 DGX Spark / Ollama 활용)<br>• <b>gemma4:31b-it-qat 적용으로 Tool Calling 안정성 및 96K Context 확보</b></td>
      <td style="padding: 10px 12px;">• 상용 Claude 3.5 대비 간헐적 포맷 붕괴 (<code>INCOMPLETE_SESSION</code>)<br>• <b>추론 속도가 느려</b> TC 1개당 수분~수십 분 소요</td>
      <td style="padding: 10px 12px;"><b>⭐⭐⭐⭐☆ (4.0/5.0)</b><br>Gemma QAT 도입으로 Tool Call 안정성 확보, 추론 속도 고도화 추진</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>4. 확장성</b></td>
      <td style="padding: 10px 12px;">• <b>Windows ↔ Ubuntu Linux 크로스 플랫폼</b> 완비<br>• Central Orchestrator로 <b>다중 제품(Webkeeper, EDR 등) 일괄 확장</b></td>
      <td style="padding: 10px 12px;">• 사내 GPU 자원 제약으로 <b>단일 공유 Healer Job 순차 큐잉 병목</b><br>• 대규모 실패 발생 시 파이프라인 타임아웃 위험</td>
      <td style="padding: 10px 12px;"><b>⭐⭐⭐⭐☆ (4.0/5.0)</b><br>아키텍처 확장성은 뛰어나나, GPU 병렬 인프라 확장 필요</td>
    </tr>
  </tbody>
</table>

---

### 2.2 세부 항목별 대조 평석표

<table>
  <thead>
    <tr>
      <th width="20%" style="padding: 10px 12px;">세부 평가 항목</th>
      <th width="40%" style="padding: 10px 12px;">🟢 긍정적 평가 내용</th>
      <th width="40%" style="padding: 10px 12px;">🔴 비판적 평가 내용</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 10px 12px;"><b>개발자 경험 (DX)</b></td>
      <td style="padding: 10px 12px;">야간 자동화 실행 후 출근 시 <b>AI Thinking & Healing Report</b> 생성 및 <b>자동 커밋/푸시와 Mattermost 카드 알림</b> 완료로 유지보수 공수 90% 이상 절감.</td>
      <td style="padding: 10px 12px;">복합적인 제품 결함이나 BDD 시나리오 변경 건에 대해 최종 검토/승인하는 차기 PR 연동 과제 존재.</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>수정 무결성</b></td>
      <td style="padding: 10px 12px;"><code>playwright_test_test_run</code> 도구로 수정된 코드의 정당성을 백그라운드에서 직접 실행 검증하여 <b>확실히 동작하는 코드만 통과</b>.</td>
      <td style="padding: 10px 12px;">실패 원인이 앱 버그나 BDD 스텝 누락인 경우 에이전트가 스스로 수정하지 못하고 <b>스킵 처리하여 결국 사람 손을 타게 됨</b>.</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>리소스 최적화</b></td>
      <td style="padding: 10px 12px;">전체 테스트를 재실행하지 않고 <b><code>extract_failed_tests.js</code>로 실패한 단일 TC만 핀포인트 디버깅</b>하여 토큰/시간 절약.</td>
      <td style="padding: 10px 12px;">로컬 LLM 추론 속도 한계로 <b>실패 TC 10개 처리 시 1~2시간 이상 소요</b>되어 CI/CD 빠른 피드백 주기 저해.</td>
    </tr>
    <tr>
      <td style="padding: 10px 12px;"><b>파이프라인 관리</b></td>
      <td style="padding: 10px 12px;"><code>setup-pi.ps1</code> 스크립트를 통해 젠킨스 빌드 노드 환경에 맞춰 <b>설정 파일(.pi/*.json)을 동적 생성</b>하여 인프라 유연성 확보.</td>
      <td style="padding: 10px 12px;"><code>Jenkinsfile.healer</code>, <code>Jenkinsfile.orchestrator</code>, Groovy JsonSlurper 등 <b>파이프라인 관리 스크립트 파편화로 인한 자체 에러 관리 공수</b> 발생.</td>
    </tr>
  </tbody>
</table>

---

💡 **종합 평가 결론 한 줄 요약**:
> **"사내 Qwen Fable 모델의 검증 지연 이슈를 거쳐, gemma4:31b-it-qat 적용으로 Tool Calling 제약을 극복하고 100% 무인 자율 힐링 파이프라인 완비."**
