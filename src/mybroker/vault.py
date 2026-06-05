from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mybroker.topics import DEFAULT_TOPICS_PATH, load_topic_config


KNOWLEDGE_VAULT_COMPILE_SCHEMA_VERSION = "knowledge_vault_compile.v1"
DEFAULT_VAULT_ROOT = Path("research-vault")
DEFAULT_VAULT_RAW_DIR = DEFAULT_VAULT_ROOT / "raw"
DEFAULT_VAULT_WIKI_DIR = DEFAULT_VAULT_ROOT / "wiki"
DEFAULT_VAULT_OUTPUT_DIR = DEFAULT_VAULT_ROOT / "output"
DEFAULT_VAULT_COMPILE_OUTPUT = Path("reports/vault/compile.json")
DEFAULT_VAULT_SURFACE_OUTPUT = Path("reports/product/vault.html")


def init_knowledge_vault(*, root: str | Path = DEFAULT_VAULT_ROOT) -> dict[str, Any]:
    vault_root = Path(root)
    raw_dir = vault_root / "raw"
    wiki_dir = vault_root / "wiki"
    output_dir = vault_root / "output"
    for directory in [raw_dir, wiki_dir, output_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    master_index = wiki_dir / "_master-index.md"
    if not master_index.exists():
        master_index.write_text(
            "# Knowledge Base Index\n\nTopics will be listed here as they are created.\n",
            encoding="utf-8",
        )
    return {
        "schema_version": "knowledge_vault_init.v1",
        "generated_at": _now(),
        "root": vault_root.as_posix(),
        "raw_dir": raw_dir.as_posix(),
        "wiki_dir": wiki_dir.as_posix(),
        "output_dir": output_dir.as_posix(),
        "master_index": master_index.as_posix(),
        "policy": "research_only",
    }


def compile_knowledge_vault(
    *,
    raw_dir: str | Path = DEFAULT_VAULT_RAW_DIR,
    wiki_dir: str | Path = DEFAULT_VAULT_WIKI_DIR,
    output_path: str | Path = DEFAULT_VAULT_COMPILE_OUTPUT,
    surface_path: str | Path = DEFAULT_VAULT_SURFACE_OUTPUT,
    topics_path: str | Path = DEFAULT_TOPICS_PATH,
) -> dict[str, Any]:
    raw_root = Path(raw_dir)
    wiki_root = Path(wiki_dir)
    wiki_root.mkdir(parents=True, exist_ok=True)
    interests = _load_interests(topics_path)
    compiled = []
    for source in _raw_sources(raw_root):
        text = source.read_text(encoding="utf-8", errors="replace")
        note = _compile_note(source=source, text=text, interests=interests, wiki_root=wiki_root)
        _write_note(note)
        compiled.append(_note_record(note))
    topics = _topic_records(compiled)
    _write_indexes(wiki_root=wiki_root, topics=topics)
    payload = {
        "schema_version": KNOWLEDGE_VAULT_COMPILE_SCHEMA_VERSION,
        "generated_at": _now(),
        "raw_dir": raw_root.as_posix(),
        "wiki_dir": wiki_root.as_posix(),
        "topics_path": Path(topics_path).as_posix(),
        "compiled_count": len(compiled),
        "topic_count": len(topics),
        "compiled_notes": compiled,
        "topics": topics,
        "surface_path": Path(surface_path).as_posix(),
        "policy": "research_only",
        "limitations": [
            "Compilation is deterministic local filing, not an investment recommendation.",
            "Raw files are not deleted or moved; inspect source_path before relying on a note.",
        ],
    }
    _write_json(payload, output_path)
    _write_surface(payload, surface_path)
    return payload


def validate_knowledge_vault_compile_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != KNOWLEDGE_VAULT_COMPILE_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {payload.get('schema_version')}")
    if payload.get("compiled_count", 0) != len(payload.get("compiled_notes", [])):
        errors.append("compiled_count must match compiled_notes length")
    if payload.get("topic_count", 0) != len(payload.get("topics", [])):
        errors.append("topic_count must match topics length")
    if payload.get("policy") != "research_only":
        errors.append("policy must be research_only")
    for index, note in enumerate(payload.get("compiled_notes", [])):
        for field in ["source_path", "wiki_path", "topic_id", "title", "source_hash", "key_takeaways"]:
            if field not in note:
                errors.append(f"compiled_notes[{index}] missing {field}")
        if not note.get("key_takeaways"):
            errors.append(f"compiled_notes[{index}] key_takeaways must not be empty")
    return errors


def validate_knowledge_vault_compile_file(path: str | Path) -> list[str]:
    return validate_knowledge_vault_compile_payload(json.loads(Path(path).read_text(encoding="utf-8")))


def _compile_note(*, source: Path, text: str, interests: list[dict[str, Any]], wiki_root: Path) -> dict[str, Any]:
    title = _title_for(source=source, text=text)
    topic = _classify_topic(text=f"{title}\n{text}", interests=interests)
    slug = _slug(title)
    topic_dir = wiki_root / topic["topic_id"]
    wiki_path = topic_dir / f"{slug}.md"
    return {
        "source": source,
        "wiki_path": wiki_path,
        "topic_id": topic["topic_id"],
        "topic_name": topic["name"],
        "title": title,
        "source_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "key_takeaways": _key_takeaways(text),
        "word_count": len(text.split()),
    }


def _write_note(note: dict[str, Any]) -> None:
    target = note["wiki_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    takeaways = "\n".join(f"- {item}" for item in note["key_takeaways"])
    target.write_text(
        "\n".join([
            f"# {note['title']}",
            "",
            f"Source: {note['source'].as_posix()}",
            f"Topic: {note['topic_name']}",
            f"Source hash: {note['source_hash']}",
            "",
            "## Key Takeaways",
            takeaways,
            "",
            "## Follow-Up Questions",
            f"- What changed since the last note about {note['topic_name']}?",
            "- Which source should be checked before trusting this summary?",
            "",
        ]),
        encoding="utf-8",
    )


def _note_record(note: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_path": note["source"].as_posix(),
        "wiki_path": note["wiki_path"].as_posix(),
        "topic_id": note["topic_id"],
        "topic_name": note["topic_name"],
        "title": note["title"],
        "source_hash": note["source_hash"],
        "word_count": note["word_count"],
        "key_takeaways": note["key_takeaways"],
    }


def _topic_records(compiled: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for note in compiled:
        topic = grouped.setdefault(note["topic_id"], {
            "topic_id": note["topic_id"],
            "name": note["topic_name"],
            "note_count": 0,
            "notes": [],
        })
        topic["note_count"] += 1
        topic["notes"].append({
            "title": note["title"],
            "wiki_path": note["wiki_path"],
            "source_path": note["source_path"],
        })
    return sorted(grouped.values(), key=lambda row: row["name"])


def _write_indexes(*, wiki_root: Path, topics: list[dict[str, Any]]) -> None:
    master_lines = ["# Knowledge Base Index", ""]
    if not topics:
        master_lines.append("Topics will be listed here as they are created.")
    for topic in topics:
        topic_dir = wiki_root / topic["topic_id"]
        topic_dir.mkdir(parents=True, exist_ok=True)
        index_path = topic_dir / "_index.md"
        master_lines.append(f"- [{topic['name']}]({topic['topic_id']}/_index.md): {topic['note_count']} notes")
        note_lines = [f"# {topic['name']}", ""]
        for note in topic["notes"]:
            note_lines.append(f"- [{note['title']}]({Path(note['wiki_path']).name})")
        index_path.write_text("\n".join(note_lines) + "\n", encoding="utf-8")
    (wiki_root / "_master-index.md").write_text("\n".join(master_lines) + "\n", encoding="utf-8")


def _write_surface(payload: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = "".join(
        "<article class='card'>"
        f"<span>{_esc(note.get('topic_name', ''))}</span>"
        f"<h2>{_esc(note.get('title', ''))}</h2>"
        f"<p>{_esc(note.get('source_path', ''))}</p>"
        "<ul>"
        + "".join(f"<li>{_esc(item)}</li>" for item in note.get("key_takeaways", [])[:3])
        + "</ul>"
        f"<a href='{_esc(note.get('wiki_path', ''))}'>wiki note</a>"
        "</article>"
        for note in payload.get("compiled_notes", [])
    ) or "<p>아직 컴파일된 raw note가 없습니다.</p>"
    target.write_text(f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MyBroker Vault</title>
<style>
:root {{ --ink:#172033; --muted:#667085; --line:#d8dee8; --panel:#f7f9fc; --accent:#1d4ed8; }}
body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:var(--ink); background:#fff; }}
main {{ max-width:980px; margin:0 auto; padding:28px 18px 48px; }}
.hero {{ border-bottom:1px solid var(--line); padding-bottom:18px; margin-bottom:18px; }}
.hero span,.card span {{ color:var(--accent); font-size:12px; font-weight:800; text-transform:uppercase; }}
h1 {{ font-size:30px; margin:6px 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:12px; }}
.card {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:14px; }}
.card h2 {{ font-size:17px; margin:6px 0; }}
.card p {{ color:var(--muted); font-size:13px; overflow-wrap:anywhere; }}
.card a {{ color:var(--accent); font-weight:700; }}
</style>
</head>
<body>
<main>
<section class="hero">
<span>Local Research Vault</span>
<h1>컴파일된 리서치 노트</h1>
<p>raw 자료를 지우지 않고 wiki note와 index로 정리한 로컬 지식베이스입니다. 투자 조언이 아니라 학습과 리서치 기억을 위한 표면입니다.</p>
<p>Compiled {payload.get('compiled_count', 0)} notes across {payload.get('topic_count', 0)} topics.</p>
</section>
<section class="grid">{rows}</section>
</main>
</body>
</html>
""", encoding="utf-8")


def _raw_sources(raw_root: Path) -> list[Path]:
    if not raw_root.exists():
        return []
    return sorted(
        path for path in raw_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".markdown", ".txt"} and not path.name.startswith(".")
    )


def _load_interests(topics_path: str | Path) -> list[dict[str, Any]]:
    path = Path(topics_path)
    if not path.exists():
        return []
    return load_topic_config(path).get("interests", [])


def _classify_topic(*, text: str, interests: list[dict[str, Any]]) -> dict[str, str]:
    lower = text.lower()
    best_score = 0
    best = None
    for interest in interests:
        keywords = [str(item).lower() for item in interest.get("keywords", [])]
        keywords.extend(str(item).lower() for item in interest.get("target_topics", []))
        score = sum(1 for keyword in keywords if keyword and keyword in lower)
        if score > best_score:
            best_score = score
            best = interest
    if best:
        return {"topic_id": best.get("topic_id", _slug(best.get("name", "topic"))), "name": best.get("name", "Topic")}
    return {"topic_id": "general-research", "name": "General Research"}


def _title_for(*, source: Path, text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or source.stem
        if stripped:
            return stripped[:80]
    return source.stem


def _key_takeaways(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("-*0123456789. ").strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)
        if len(lines) >= 5:
            break
    return lines or ["No readable text was found in the raw note."]


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return normalized[:80] or "untitled"


def _write_json(payload: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def _esc(value: Any) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
