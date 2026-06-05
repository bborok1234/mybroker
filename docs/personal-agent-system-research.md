# Personal Agent System Research

Updated: 2026-06-06

## 결론

MyBroker의 1차 방향은 웹앱/서버/계좌 연결이 아니다. 현재 개인 에이전트 사례에서 반복되는 강한 패턴은 로컬 작업공간, 장기 기억, 스케줄러, 메시지/폰 handoff, 짧은 operator command, artifact proof, 안전 게이트다.

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
