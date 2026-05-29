# Free Public Evidence Sources

This matrix classifies public sources for beginner-first market simulation. The first
implementation prioritizes no-key, local-cache friendly sources so runs are reproducible.

| Source | Access | Auth | Practical constraint | MyBroker use |
| --- | --- | --- | --- | --- |
| SEC EDGAR | HTTPS JSON submissions/companyfacts | No key, User-Agent required live | US issuer focus, filing interpretation | Company events, fundamentals, risk language |
| GDELT | DOC 2.0/GKG APIs or cached JSON | No key | Noisy news, dedupe needed | Narrative/event graph |
| Stooq | CSV downloads or cached CSV | No key | Symbol and adjustment validation | Market trend/risk context |
| FRED | HTTPS API | Free API key | Macro series curation and revisions | Macro regime and scenario triggers |
| Alpha Vantage | HTTPS API | Free API key | Free-tier rate limits | Optional market/indicator fallback |
| Nasdaq Data Link | API/downloads | Free account/key for many flows | Free/premium datasets mixed | Optional curated datasets after license review |

## Source Anchors

- SEC EDGAR API documentation: https://www.sec.gov/edgar/sec-api-documentation
- FRED API key documentation: https://fred.stlouisfed.org/docs/api/api_key.html
- GDELT DOC 2.0 API announcement/documentation: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- Stooq historical data entry point: https://stooq.com/db/h/
- Alpha Vantage API documentation: https://www.alphavantage.co/documentation/
- Nasdaq Data Link getting started documentation: https://docs.data.nasdaq.com/docs/getting-started

## Current Decision

The proof slice uses cached SEC, GDELT, and Stooq-shaped artifacts. This proves the
normalization and simulation path without relying on API keys, live network availability,
or paid data. Live connectors can reuse the same `public_evidence_catalog.v1` schema.
