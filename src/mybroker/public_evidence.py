from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


PUBLIC_EVIDENCE_SCHEMA_VERSION = "public_evidence_catalog.v1"
DEFAULT_PUBLIC_EVIDENCE_OUTPUT = Path("reports/evidence/public-evidence-catalog.json")
DEFAULT_CACHE_ROOT = Path(__file__).resolve().parents[2] / "examples" / "public-evidence"


SOURCE_MATRIX: list[dict[str, str]] = [
    {
        "source_name": "SEC EDGAR",
        "access_method": "HTTPS JSON endpoints: submissions and companyfacts",
        "auth_requirement": "No API key; descriptive User-Agent required for live use",
        "constraints": "US-listed company coverage; filing latency; structured facts vary by issuer",
        "coverage": "Company filings, company facts, filing metadata",
        "freshness": "Near filing publication time",
        "data_quality_risk": "Narrative text and XBRL tags need issuer-aware interpretation",
        "license_usage_concern": "Public SEC data; comply with fair access and User-Agent policy",
        "mybroker_use_case": "Company-specific evidence, event catalysts, risk language, fundamentals context",
        "implementation_priority": "high",
    },
    {
        "source_name": "FRED",
        "access_method": "HTTPS API",
        "auth_requirement": "Free API key",
        "constraints": "Macro series selection and release calendars must be curated",
        "coverage": "Rates, inflation, labor, GDP, credit, macro indicators",
        "freshness": "Official release dependent",
        "data_quality_risk": "Series revisions and units can be misunderstood by beginners",
        "license_usage_concern": "Check FRED terms and attribution requirements",
        "mybroker_use_case": "Macro regime context and scenario branch triggers",
        "implementation_priority": "medium",
    },
    {
        "source_name": "GDELT",
        "access_method": "DOC 2.0 API / GKG / cached JSON",
        "auth_requirement": "No API key",
        "constraints": "High noise; query design and deduping matter",
        "coverage": "Global news, events, themes, locations, tone",
        "freshness": "Near real time",
        "data_quality_risk": "News duplication, source bias, and weak relevance can distort narratives",
        "license_usage_concern": "Respect GDELT use guidance and source publisher rights",
        "mybroker_use_case": "Narrative/event graph and persona disagreement evidence",
        "implementation_priority": "high",
    },
    {
        "source_name": "Stooq",
        "access_method": "CSV download / cached CSV",
        "auth_requirement": "No API key",
        "constraints": "Coverage and symbols need validation; not an official exchange feed",
        "coverage": "Historical OHLCV market data",
        "freshness": "Market-data dependent; often delayed/end-of-day",
        "data_quality_risk": "Corporate actions, symbol mapping, and stale downloads must be checked",
        "license_usage_concern": "Confirm use terms before redistribution",
        "mybroker_use_case": "Price context, trend/risk evidence, scenario validation hints",
        "implementation_priority": "high",
    },
    {
        "source_name": "Alpha Vantage free tier",
        "access_method": "HTTPS API",
        "auth_requirement": "Free API key",
        "constraints": "Rate-limited free tier; terms and output size restrictions",
        "coverage": "Market prices, indicators, some economic/company data",
        "freshness": "Endpoint dependent",
        "data_quality_risk": "Free-tier throttling and adjusted/unadjusted data choices",
        "license_usage_concern": "Follow Alpha Vantage terms and attribution requirements",
        "mybroker_use_case": "Fallback market data and technical indicators",
        "implementation_priority": "low",
    },
    {
        "source_name": "Nasdaq Data Link",
        "access_method": "HTTPS API / dataset downloads",
        "auth_requirement": "Free account/API key for many flows",
        "constraints": "Free and premium datasets mixed; dataset-specific terms",
        "coverage": "Curated financial, economic, and alternative datasets",
        "freshness": "Dataset dependent",
        "data_quality_risk": "Dataset availability and licensing can change",
        "license_usage_concern": "Dataset-specific license controls redistribution",
        "mybroker_use_case": "Optional curated datasets after license review",
        "implementation_priority": "low",
    },
]


@dataclass(frozen=True)
class PublicEvidenceItem:
    item_id: str
    source_name: str
    evidence_type: str
    title: str
    published_at: str
    url: str
    text: str
    topics: list[str]
    entities: list[str]
    freshness_status: str


class PublicEvidenceAdapter(Protocol):
    adapter_id: str
    source_name: str

    def load_items(self) -> list[PublicEvidenceItem]:
        ...


class GdeltCachedAdapter:
    adapter_id = "gdelt_cached_v1"
    source_name = "GDELT"

    def __init__(self, path: str | Path = DEFAULT_CACHE_ROOT / "gdelt-ai-news.json") -> None:
        self.path = Path(path)

    def load_items(self) -> list[PublicEvidenceItem]:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        items = []
        for index, article in enumerate(payload.get("articles", []), start=1):
            text = " ".join([article.get("title", ""), article.get("summary", "")]).strip()
            items.append(
                PublicEvidenceItem(
                    item_id=f"gdelt-{index}",
                    source_name=self.source_name,
                    evidence_type="news_narrative",
                    title=article.get("title", f"GDELT article {index}"),
                    published_at=article.get("published_at", ""),
                    url=article.get("url", ""),
                    text=text,
                    topics=_detect_topics(text),
                    entities=article.get("entities", []),
                    freshness_status="sample_cache",
                )
            )
        return items


class StooqCachedAdapter:
    adapter_id = "stooq_cached_v1"
    source_name = "Stooq"

    def __init__(self, path: str | Path = DEFAULT_CACHE_ROOT / "stooq-spy.csv") -> None:
        self.path = Path(path)

    def load_items(self) -> list[PublicEvidenceItem]:
        rows = []
        with self.path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                rows.append(row)
        if len(rows) < 2:
            return []
        first = rows[0]
        last = rows[-1]
        symbol = last.get("Symbol", "SPY")
        first_close = float(first["Close"])
        last_close = float(last["Close"])
        change = ((last_close - first_close) / first_close) * 100
        direction = "상승" if change >= 0 else "하락"
        text = (
            f"{symbol} market proxy moved {direction} {change:.2f}% from {first.get('Date')} to {last.get('Date')}. "
            "This price evidence helps test whether news narratives align with broad market risk appetite, rates pressure, and volatility."
        )
        return [
            PublicEvidenceItem(
                item_id=f"stooq-{symbol.lower()}-trend",
                source_name=self.source_name,
                evidence_type="market_price_context",
                title=f"{symbol} broad market trend sample",
                published_at=last.get("Date", ""),
                url="https://stooq.com/",
                text=text,
                topics=_detect_topics(text),
                entities=[symbol, "broad market"],
                freshness_status="sample_cache",
            )
        ]


class SecCachedAdapter:
    adapter_id = "sec_cached_v1"
    source_name = "SEC EDGAR"

    def __init__(self, path: str | Path = DEFAULT_CACHE_ROOT / "sec-aapl-submissions.json") -> None:
        self.path = Path(path)

    def load_items(self) -> list[PublicEvidenceItem]:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        company = payload.get("name", "Unknown issuer")
        filings = payload.get("filings", {}).get("recent", [])
        items = []
        for index, filing in enumerate(filings, start=1):
            form = filing.get("form", "")
            text = (
                f"{company} filed {form} on {filing.get('filingDate', '')}. "
                f"Business context: {filing.get('description', '')}. "
                "This public filing evidence can anchor company-specific risk, consumer demand, supply chain, and AI infrastructure narratives."
            )
            items.append(
                PublicEvidenceItem(
                    item_id=f"sec-{index}",
                    source_name=self.source_name,
                    evidence_type="company_filing",
                    title=f"{company} {form}",
                    published_at=filing.get("filingDate", ""),
                    url=filing.get("url", "https://www.sec.gov/edgar/search/"),
                    text=text,
                    topics=_detect_topics(text),
                    entities=[company, form],
                    freshness_status="sample_cache",
                )
            )
        return items


ADAPTERS = {
    "gdelt-sample": GdeltCachedAdapter,
    "stooq-sample": StooqCachedAdapter,
    "sec-sample": SecCachedAdapter,
}


def build_public_evidence_catalog(source_ids: list[str] | None = None) -> dict[str, Any]:
    selected = source_ids or ["gdelt-sample", "stooq-sample", "sec-sample"]
    items: list[PublicEvidenceItem] = []
    source_status = []
    for source_id in selected:
        if source_id not in ADAPTERS:
            raise ValueError(f"unknown public evidence source: {source_id}")
        adapter = ADAPTERS[source_id]()
        adapter_items = adapter.load_items()
        items.extend(adapter_items)
        source_status.append({
            "source_id": source_id,
            "source_name": adapter.source_name,
            "adapter_id": adapter.adapter_id,
            "item_count": str(len(adapter_items)),
            "freshness_status": "sample_cache",
        })
    graph = build_public_evidence_graph(items)
    return {
        "schema_version": PUBLIC_EVIDENCE_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "sample_cache",
        "source_status": source_status,
        "source_matrix": SOURCE_MATRIX,
        "items": [asdict(item) for item in items],
        "graph": graph,
        "feasibility": evaluate_feasibility(items, graph),
    }


def build_public_evidence_graph(items: list[PublicEvidenceItem]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    for item in items:
        source_node = f"source:{item.source_name}"
        nodes[source_node] = {"id": source_node, "label": item.source_name, "kind": "source"}
        for topic in item.topics:
            topic_node = f"topic:{topic}"
            nodes[topic_node] = {"id": topic_node, "label": topic, "kind": "topic"}
            edges.append({"source": source_node, "target": topic_node, "relation": "supports"})
        for entity in item.entities:
            entity_node = f"entity:{entity}"
            nodes[entity_node] = {"id": entity_node, "label": entity, "kind": "entity"}
            edges.append({"source": source_node, "target": entity_node, "relation": "mentions"})
    topic_labels = sorted(node["label"] for node in nodes.values() if node["kind"] == "topic")
    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "narrative_summary": f"Public evidence connects {len(items)} items across topics: {', '.join(topic_labels)}.",
    }


def evaluate_feasibility(items: list[PublicEvidenceItem], graph: dict[str, Any]) -> dict[str, Any]:
    sources = {item.source_name for item in items}
    topics = {topic for item in items for topic in item.topics}
    blockers = []
    if len(sources) < 2:
        blockers.append("need_at_least_two_sources")
    if len(topics) < 3:
        blockers.append("topic_coverage_too_thin")
    if not any(item.evidence_type == "news_narrative" for item in items):
        blockers.append("missing_news_narrative")
    status = "meaningful" if not blockers else "weak"
    return {
        "status": status,
        "reasons": [
            f"{len(sources)} source families observed",
            f"{len(topics)} market topics observed",
            f"{len(graph.get('nodes', []))} graph nodes and {len(graph.get('edges', []))} edges generated",
        ],
        "blockers": blockers,
        "next_gaps": ["live refresh policy", "deduplication", "source licensing review", "LLM-free entity extraction quality"],
    }


def write_public_evidence_catalog(catalog: dict[str, Any], path: str | Path = DEFAULT_PUBLIC_EVIDENCE_OUTPUT) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def load_public_evidence_catalog(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_public_evidence_catalog_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "generated_at", "mode", "source_status", "source_matrix", "items", "graph", "feasibility"}
    missing = sorted(required.difference(payload))
    if missing:
        errors.append(f"missing required public evidence catalog fields: {', '.join(missing)}")
    if payload.get("schema_version") != PUBLIC_EVIDENCE_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if len(payload.get("items", [])) < 2:
        errors.append("items must contain evidence from at least two records")
    source_names = {item.get("source_name") for item in payload.get("items", [])}
    if len(source_names) < 2:
        errors.append("catalog must include at least two source families")
    graph = payload.get("graph", {})
    if not graph.get("nodes") or not graph.get("edges"):
        errors.append("graph.nodes and graph.edges must not be empty")
    if payload.get("feasibility", {}).get("status") not in {"meaningful", "weak", "blocked"}:
        errors.append("feasibility.status must be meaningful, weak, or blocked")
    return errors


def validate_public_evidence_catalog_file(path: str | Path) -> list[str]:
    return validate_public_evidence_catalog_payload(load_public_evidence_catalog(path))


def _detect_topics(text: str) -> list[str]:
    lowered = text.lower()
    mapping = {
        "ai_infrastructure": ["ai", "artificial intelligence", "data center", "gpu", "cloud"],
        "semiconductors": ["semiconductor", "chip", "memory", "supply chain"],
        "rates": ["rate", "yield", "fed", "treasury"],
        "inflation": ["inflation", "cpi", "prices"],
        "consumer": ["consumer", "demand", "retail", "iphone"],
        "risk": ["risk", "volatility", "pressure", "uncertainty", "filing"],
    }
    topics = [topic for topic, keywords in mapping.items() if any(keyword in lowered for keyword in keywords)]
    return topics or ["risk"]
