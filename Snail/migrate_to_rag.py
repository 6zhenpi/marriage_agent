import re
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

SOURCE_ROOT = Path(r"d:\project\marriage_agent\Collected legal data")
TARGET_ROOT = Path(r"d:\project\marriage_agent\RAGdata")
METADATA_SOURCE = SOURCE_ROOT / "metadata.json"

CHUNK_COUNTER = 0


def next_chunk_id(prefix: str) -> str:
    global CHUNK_COUNTER
    CHUNK_COUNTER += 1
    return f"{prefix}_{CHUNK_COUNTER:04d}"


def md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def parse_law_article(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    lines = text.strip().split("\n")

    meta = {}
    for line in lines:
        if line.startswith("法律名称："):
            meta["law_name"] = line.replace("法律名称：", "").strip()
        elif line.startswith("编章："):
            meta["part"] = line.replace("编章：", "").strip()
        elif line.startswith("条文编号："):
            meta["article_number"] = line.replace("条文编号：", "").strip()

    content_lines = []
    in_content = False
    for line in lines:
        if in_content:
            content_lines.append(line)
        if line.startswith("条文编号："):
            in_content = True
    content = "\n".join(content_lines).strip()

    if not content:
        return []

    chunk_id = next_chunk_id("law")
    chunk_text = f"{meta.get('law_name', '')} {meta.get('part', '')} {meta.get('article_number', '')} {content}"

    record = {
        "chunk_id": chunk_id,
        "category": "法律条文",
        "source_file": filepath.name,
        "law_name": meta.get("law_name", ""),
        "part": meta.get("part", ""),
        "article_number": meta.get("article_number", ""),
        "content": content,
        "chunk_text": chunk_text,
        "content_md5": md5(content),
        "migrated_at": datetime.now().isoformat(),
    }
    return [record]


def parse_judicial_interpretation(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    lines = text.strip().split("\n")

    meta = {}
    for line in lines:
        if line.startswith("标题："):
            meta["title"] = line.replace("标题：", "").strip()
        elif line.startswith("文号："):
            meta["document_number"] = line.replace("文号：", "").strip()
        elif line.startswith("生效日期："):
            meta["effective_date"] = line.replace("生效日期：", "").strip()

    article_pattern = re.compile(r"^第(\d+)条\s+(.+)$")
    articles = []
    current_num = None
    current_text = ""

    in_content = False
    for line in lines:
        if line.startswith("来源网址："):
            in_content = True
            continue
        if not in_content:
            continue

        m = article_pattern.match(line.strip())
        if m:
            if current_num is not None:
                articles.append((current_num, current_text.strip()))
            current_num = m.group(1)
            current_text = m.group(2)
        elif current_num is not None and line.strip():
            current_text += " " + line.strip()

    if current_num is not None:
        articles.append((current_num, current_text.strip()))

    chunks = []
    for art_num, art_text in articles:
        chunk_id = next_chunk_id("jud")
        chunk_text = f"{meta.get('title', '')} 第{art_num}条 {art_text}"

        record = {
            "chunk_id": chunk_id,
            "category": "司法解释",
            "source_file": filepath.name,
            "title": meta.get("title", ""),
            "document_number": meta.get("document_number", ""),
            "effective_date": meta.get("effective_date", ""),
            "article_number": f"第{art_num}条",
            "content": art_text,
            "chunk_text": chunk_text,
            "content_md5": md5(art_text),
            "migrated_at": datetime.now().isoformat(),
        }
        chunks.append(record)

    return chunks


def parse_court_case(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    lines = text.strip().split("\n")

    meta = {}
    for line in lines:
        for key in ["案例编号", "标题", "法院", "法院级别", "案号", "争议类型", "子类型", "省份", "发布日期", "是否指导性案例"]:
            if line.startswith(f"{key}："):
                meta[key] = line.replace(f"{key}：", "").strip()

    sections = {}
    current_section = None
    section_pattern = re.compile(r"^【(.+)】$")

    for line in lines:
        m = section_pattern.match(line.strip())
        if m:
            current_section = m.group(1)
            sections[current_section] = []
        elif current_section is not None and line.strip():
            sections[current_section].append(line.strip())

    for key in sections:
        sections[key] = "\n".join(sections[key])

    facts = sections.get("案件事实", "")
    reasoning = sections.get("法院说理", "")
    judgment = sections.get("裁判结果", "")
    plaintiff = sections.get("原告诉请", "")
    defendant = sections.get("被告诉辩", "")
    legal_basis = sections.get("法律依据", "")
    keywords = sections.get("关键词", "")

    embedding_text = f"{facts} {reasoning} {judgment}"

    chunk_id = next_chunk_id("case")
    chunk_text = f"{meta.get('标题', '')} {meta.get('争议类型', '')} {embedding_text}"

    record = {
        "chunk_id": chunk_id,
        "category": "裁判案例",
        "source_file": filepath.name,
        "case_id": meta.get("案例编号", ""),
        "title": meta.get("标题", ""),
        "court": meta.get("法院", ""),
        "court_level": meta.get("法院级别", ""),
        "case_number": meta.get("案号", ""),
        "dispute_type": meta.get("争议类型", ""),
        "sub_type": meta.get("子类型", ""),
        "province": meta.get("省份", ""),
        "release_date": meta.get("发布日期", ""),
        "is_guiding_case": meta.get("是否指导性案例", "否") == "是",
        "facts_summary": facts,
        "plaintiff_claim": plaintiff,
        "defendant_defense": defendant,
        "court_reasoning": reasoning,
        "judgment_result": judgment,
        "legal_basis": [b.strip() for b in legal_basis.split(",") if b.strip()],
        "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
        "content": embedding_text,
        "chunk_text": chunk_text,
        "content_md5": md5(embedding_text),
        "migrated_at": datetime.now().isoformat(),
    }
    return [record]


def migrate():
    print("=" * 60)
    print("  RAGdata 数据迁移工具")
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_chunks = []
    source_stats = {"法律条文": 0, "司法解释": 0, "裁判案例": 0}
    target_stats = {"法律条文": 0, "司法解释": 0, "裁判案例": 0}

    law_dir = SOURCE_ROOT / "法律条文"
    if law_dir.exists():
        law_files = sorted([f for f in law_dir.iterdir() if f.suffix == ".txt"])
        source_stats["法律条文"] = len(law_files)
        print(f"\n[1/3] 处理法律条文: {len(law_files)} 个文件")

        law_chunks = []
        for f in law_files:
            chunks = parse_law_article(f)
            law_chunks.extend(chunks)
        all_chunks.extend(law_chunks)
        target_stats["法律条文"] = len(law_chunks)

        law_output = TARGET_ROOT / "法律条文" / "law_articles.json"
        law_output.parent.mkdir(parents=True, exist_ok=True)
        law_output.write_text(
            json.dumps(law_chunks, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  → 生成 {len(law_chunks)} 个 chunk, 写入 law_articles.json")

        for f in law_files:
            dest = TARGET_ROOT / "法律条文" / "raw" / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)

    jud_dir = SOURCE_ROOT / "司法解释"
    if jud_dir.exists():
        jud_files = sorted([f for f in jud_dir.iterdir() if f.suffix == ".txt"])
        source_stats["司法解释"] = len(jud_files)
        print(f"\n[2/3] 处理司法解释: {len(jud_files)} 个文件")

        jud_chunks = []
        for f in jud_files:
            chunks = parse_judicial_interpretation(f)
            jud_chunks.extend(chunks)
        all_chunks.extend(jud_chunks)
        target_stats["司法解释"] = len(jud_chunks)

        jud_output = TARGET_ROOT / "司法解释" / "judicial_interpretations.json"
        jud_output.parent.mkdir(parents=True, exist_ok=True)
        jud_output.write_text(
            json.dumps(jud_chunks, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  → 生成 {len(jud_chunks)} 个 chunk, 写入 judicial_interpretations.json")

        for f in jud_files:
            dest = TARGET_ROOT / "司法解释" / "raw" / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)

    case_dir = SOURCE_ROOT / "裁判案例"
    if case_dir.exists():
        case_files = sorted([f for f in case_dir.iterdir() if f.suffix == ".txt"])
        source_stats["裁判案例"] = len(case_files)
        print(f"\n[3/3] 处理裁判案例: {len(case_files)} 个文件")

        case_chunks = []
        for f in case_files:
            chunks = parse_court_case(f)
            case_chunks.extend(chunks)
        all_chunks.extend(case_chunks)
        target_stats["裁判案例"] = len(case_chunks)

        case_output = TARGET_ROOT / "裁判案例" / "court_cases.json"
        case_output.parent.mkdir(parents=True, exist_ok=True)
        case_output.write_text(
            json.dumps(case_chunks, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  → 生成 {len(case_chunks)} 个 chunk, 写入 court_cases.json")

        for f in case_files:
            dest = TARGET_ROOT / "裁判案例" / "raw" / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)

    all_output = TARGET_ROOT / "all_chunks.jsonl"
    with open(all_output, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"\n  → 合并写入 all_chunks.jsonl ({len(all_chunks)} 条)")

    manifest = {
        "migrated_at": datetime.now().isoformat(),
        "source_root": str(SOURCE_ROOT),
        "target_root": str(TARGET_ROOT),
        "source_file_counts": source_stats,
        "target_chunk_counts": target_stats,
        "total_chunks": len(all_chunks),
        "collections": {
            "law_articles": {
                "file": "法律条文/law_articles.json",
                "count": target_stats["法律条文"],
                "fields": ["chunk_id", "law_name", "part", "article_number", "content", "chunk_text"],
            },
            "judicial_interpretations": {
                "file": "司法解释/judicial_interpretations.json",
                "count": target_stats["司法解释"],
                "fields": ["chunk_id", "title", "document_number", "article_number", "content", "chunk_text"],
            },
            "court_cases": {
                "file": "裁判案例/court_cases.json",
                "count": target_stats["裁判案例"],
                "fields": ["chunk_id", "case_id", "title", "dispute_type", "facts_summary", "court_reasoning", "judgment_result", "content", "chunk_text"],
            },
        },
    }
    manifest_path = TARGET_ROOT / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("  迁移完成")
    print("=" * 60)
    print(f"  源文件: 法律条文 {source_stats['法律条文']}, 司法解释 {source_stats['司法解释']}, 裁判案例 {source_stats['裁判案例']}")
    print(f"  生成chunk: 法律条文 {target_stats['法律条文']}, 司法解释 {target_stats['司法解释']}, 裁判案例 {target_stats['裁判案例']}")
    print(f"  总计: {len(all_chunks)} 个 chunk")
    print("=" * 60)

    return manifest


if __name__ == "__main__":
    migrate()
