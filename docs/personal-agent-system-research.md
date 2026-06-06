# Personal Agent System Research

Updated: 2026-06-06

## 결론

MyBroker의 1차 방향은 웹앱/서버/계좌 연결이 아니다. 현재 개인 에이전트 사례에서 반복되는 강한 패턴은 로컬 작업공간, 장기 기억, 스케줄러, 메시지/폰 handoff, 짧은 operator command, artifact proof, 안전 게이트다.

## 2026-06-06 추가 리서치 결론

어제의 최선이 오늘의 최선이 아닐 수 있다는 전제는 맞다. 다만 매일 바뀌는 것은
"어떤 도구를 붙일까"이고, 덜 바뀌는 것은 운영 원칙이다. 최신 개인 에이전트 사례에서
반복되는 실전 패턴은 다음이다.

1. 웹앱을 먼저 만들지 않는다. 먼저 매일 도는 로컬 작업자, 메모리, 스케줄, 산출물,
   폰 접근, 승인 루프를 만든다.
2. 사용자는 자료를 직접 잘 넣지 못한다. 시스템이 오늘 볼 주제와 근거 수집 계획을 먼저
   제안하고, 사람은 짧게 승인/거절/더보기만 한다.
3. 고급 프론트엔드보다 중요한 것은 "오늘 무엇을 믿고 읽을지"를 보여주는 첫 화면이다.
4. 새 도구는 바로 제품에 섞지 않는다. pattern radar -> dry run -> proof artifact ->
   daily loop 채택 순서로 승격한다.
5. 브라우저/메시징/라이브 데이터는 강력하지만 공격면도 커진다. 기본값은 read-only,
   local-first, no public exposure, scoped approval이어야 한다.

## 최신 사례에서 얻은 운영 패턴

| 사례 | 관찰 | MyBroker 판단 |
| --- | --- | --- |
| Hermes Agent | 스스로 skill을 만들고 개선하는 closed learning loop, 과거 대화 검색, scheduled automation, Telegram/Slack/CLI gateway, 원격/저비용 persistent runtime을 강조한다. | MyBroker는 범용 비서가 아니라 daily analyst appliance로 좁힌다. skill 생성은 바로 자동 채택하지 말고 eval과 artifact proof 뒤에만 승격한다. |
| OpenClaw | launchd/systemd daemon, multi-channel inbox, pairing/allowlist, isolated workspaces, host tool 권한과 sandbox 경계를 명시한다. | 폰 접근은 private-first가 맞다. unknown sender, public DM, public tunnel은 기본 차단한다. `phone-access-verify` 같은 no-effect proof를 유지한다. |
| MiroFish | knowledge graph, swarm/multi-agent simulation, social/future prediction UX, frontend+backend 제품면을 가진다. | 제품 UX는 참고하되, 지금은 전용 서버보다 `today/home/brief` HTML artifact가 맞다. 핵심은 market/narrative map과 beginner explanation이다. |
| TradingAgents | multi-agent debate, role별 분석, persistence/recovery, checkpoint, decision memory를 둔다. | "매수/매도 결정"은 거절하고, role council, skeptic, tutor, memory librarian, scenario path만 흡수한다. run history와 reflection은 적극 채택한다. |
| Tailscale Serve/private phone access | 로컬 산출물을 public web app으로 배포하지 않고 private tailnet에서 폰으로 읽게 할 수 있다. | `phone-access-verify`를 local proof 후보로 채택한다. 실제 `tailscale serve` 실행은 private_network_exposure 승인 뒤에만 가능하다. |
| DBOS durable workflows | workflow/step을 durable하게 기록하고, cron schedule, queue concurrency, backfill, resume을 제공한다. | launchd만으로 부족해지는 순간 DBOS류 durable workflow를 검토한다. v1은 로컬 JSON proof와 run ledger로 충분하지만, missed run/backfill이 중요해지면 도입 후보 1순위다. |
| Browser-use/Playwright MCP/Firecrawl | browser control, search/scrape, markdown extraction을 agent tool로 붙인다. | live evidence refresh에는 유용하지만 기본 실행은 금지한다. 먼저 source-refresh preflight와 approval scope를 통과한 no-key/read-only source부터 붙인다. |
| Obsidian + Claude Code finance workflow | raw/wiki/output, compile/query/audit verbs, long-term knowledge compounding을 개인 리서치에 적용한다. | 사용자가 source를 잘 고르지 못한다는 문제는 scout가 해결한다. vault는 보조 입력이고, 기본은 MyBroker가 오늘의 주제와 자료를 제안하는 방식이어야 한다. |

## MyBroker에 반영할 다음 제품 방향

### Daily Scout가 사용자 대신 시작한다

초보 사용자는 "특정 종목/섹터/이벤트 가설"을 넣기 어렵다. 따라서 MyBroker의 기본 입력은
사용자 가설이 아니라 매일의 scout 결과여야 한다.

- 오늘 시장을 이해하기 위한 1개 주제 추천
- 왜 이 주제를 봐야 하는지 3문장 설명
- 무료/공개 근거 source fan-out
- 초보자가 먼저 읽을 순서
- 약한 근거, 오래된 근거, 충돌하는 근거
- 내일 이어갈 질문

### 개인 애널리스트 직원처럼 동작한다

MyBroker의 좋은 형태는 채팅봇이나 웹앱이 아니라 매일 출근하는 로컬 애널리스트다.

1. 06:30 local run: 무료 공개 source와 캐시로 오늘의 후보 주제를 만든다.
2. 06:40 source scout: 각 후보의 근거 품질과 신선도를 평가한다.
3. 06:45 council: scout, curator, mapper, scenario analyst, skeptic, tutor가 역할별로 검토한다.
4. 06:50 brief: 폰에서 볼 daily-home/today/agenda를 만든다.
5. 사용자는 폰에서 `more`, `less`, `confusing`, `done`, `carry` 같은 짧은 응답만 남긴다.
6. 다음 run은 그 응답을 반영한다.

### 새 기술 흡수는 Pattern Radar로 제한한다

매일 새 도구를 붙이면 제품이 깨진다. 그래서 MyBroker는 외부 패턴을 다음 상태로 관리해야 한다.

- `observed`: 새 사례를 발견했지만 아직 채택하지 않음
- `candidate`: MyBroker 문제에 직접 도움 될 가능성이 있음
- `dry_run`: no-effect proof로만 시험
- `adopted`: validator와 daily loop evidence를 통과
- `rejected`: 안전/비용/복잡도 대비 가치가 낮음

## 다음 slice 제안

다음 구현은 "더 예쁜 프론트엔드"가 아니라 `daily autonomous scout`가 맞다.

목표:

- 사용자가 아무 주제도 넣지 않아도 오늘의 학습/시장 이해 주제를 추천한다.
- source freshness, evidence weakness, beginner reading order를 자동 생성한다.
- 외부 최신 agent workflow pattern도 `pattern-radar`에 넣어 채택/거절 후보를 만든다.
- 폰 첫 화면은 "오늘 무엇을 읽고, 왜 읽고, 무엇을 답하면 되는지"만 보여준다.

성공 기준:

- `mybroker appliance run` 이후 `daily-home.html`에서 오늘 주제, 읽기 순서, 근거 상태,
  짧은 응답 명령이 보인다.
- `pattern-radar.html`은 새 도구/방법론을 제품에 섞기 전에 채택 후보로만 보여준다.
- live network나 계정/유료 데이터 없이도 최소 1개 daily brief가 재현 가능하다.

## 사례별 흡수 판단

| 사례 | 확인한 패턴 | MyBroker 적용 | 판단 |
| --- | --- | --- | --- |
| Hermes Agent | built-in learning loop, persistent knowledge, past conversation search, scheduled automations, messaging gateway, subagents | daily archive, review memory, run ledger, handoff, scheduler dry-run, local proofs | adopt |
| OpenClaw | local-first gateway, multi-channel inbox, isolated agent workspaces, workspace files such as AGENTS/SOUL/TOOLS/HEARTBEAT, workspace skills | MyBroker는 broad assistant가 아니라 narrow appliance. phone links와 command surfaces만 제공 | adopt partial |
| OpenClaw security research | persistent memory plus high-privilege tool use creates attack surface: skill poisoning, cognitive manipulation, cascading failure, supply-chain risk | live network, host write, notification, credential, account, order flows stay behind separate gates | adopt as guardrail |
| MiroFish | seed evidence -> graph/simulation world -> persona/path simulation; strong visual/narrative UX | beginner-first market map, scenario paths, persona disagreement, missing evidence 표시 | adopt UX pattern only |
| TradingAgents | specialized financial analyst roles, bullish/bearish debate, risk team; explicitly research-only disclaimer | source scout, evidence curator, market mapper, scenario analyst, skeptic, tutor, memory librarian | adopt roles, reject trading execution |
| FinRobot | financial agent platform, data fetching, multi-agent report generation, HTML/PDF style output; API-key driven professional workflow | report structure and grounded multi-agent analysis are useful; paid API/account assumptions deferred | adopt partial |
| Claude Code + Obsidian finance workflow | raw/wiki/output vault, compile/query/audit verbs, browser/scraper tools, plain-language operator workflow | local vault compile, memory query/audit, copy-ready phone feedback, handoff-response-apply | adopt |
| Tailscale Serve/private phone access | private tailnet serving before public deployment | phone-access plan and verify proof only; actual serving remains separately approved | adopt partial |
| DBOS durable workflows | durable steps, queues, cron, resume, backfill | defer until launchd/run-ledger evidence shows missed-run or backfill pain | defer |
| TaskWeaver | code-first analytics agent for executable data analysis | future sandboxed simulation notebooks after artifact schemas stabilize | defer |

## 현재 MyBroker 설계 원칙

1. Daily loop first: 매일 읽고, 응답하고, 다음 날 반영되는 루프가 제품의 핵심이다.
2. Local memory first: reports, archive, vault, review/task JSONL이 개인 애널리스트의 기억이다.
3. Phone handoff first: 폰에서는 읽고 짧은 명령을 복사한다. 노트북이 그 명령을 로컬 proof로 적용한다.
4. Artifact proof first: 모든 반영은 JSON/HTML proof로 남고 validator가 확인한다.
5. No execution by default: live network, notification send, host write, credentials, account access, orders, discretionary recommendations are separate gates.

## 이번 slice에 반영한 것

Handoff 화면은 unresolved question/task를 보여주는 읽기 surface다. 하지만 기존에는 copy command가 실제 loop closure로 충분히 이어지지 않았다. 그래서 `handoff-response-apply`를 추가한다.

- review형 응답: `more "Semiconductors" "tomorrow too"` -> review memory, daily review, scout, review prompt/effect, handoff 갱신.
- task형 응답: `AT-001 complete "checked locally"` -> task status apply, task ledger, daily review, handoff 갱신.
- 두 route 모두 `operator_handoff_response_apply.v1`과 `reports/product/handoff-response-apply.html`을 남긴다.

## Sources

- https://github.com/NousResearch/hermes-agent
- https://github.com/openclaw/openclaw
- https://docs.openclaw.ai/start/openclaw
- https://arxiv.org/abs/2605.25435
- https://github.com/666ghj/MiroFish
- https://github.com/TauricResearch/TradingAgents
- https://github.com/AI4Finance-Foundation/FinRobot
- https://github.com/microsoft/TaskWeaver
- https://tailscale.com/kb/1312/serve
- https://www.dbos.dev/
