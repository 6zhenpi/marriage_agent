import os
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx"}
DATA_ROOT = Path(r"d:\project\marriage_agent\Collected legal data")
METADATA_FILE = DATA_ROOT / "metadata.json"
REJECTED_DIR = DATA_ROOT / "_rejected"

logger = logging.getLogger("snail.validator")


def _ensure_metadata():
    if not METADATA_FILE.exists():
        METADATA_FILE.write_text("[]", encoding="utf-8")
    if not REJECTED_DIR.exists():
        REJECTED_DIR.mkdir(parents=True, exist_ok=True)


def _load_metadata() -> list:
    _ensure_metadata()
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_metadata(records: list):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def validate_file_extension(file_path: str | Path) -> bool:
    ext = Path(file_path).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def validate_file_content(file_path: str | Path) -> bool:
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {path}")
        return False
    if path.stat().st_size == 0:
        logger.warning(f"Empty file: {path}")
        return False
    ext = path.suffix.lower()
    magic_map = {
        ".pdf": b"%PDF",
        ".doc": b"\xd0\xcf\x11\xe0",
        ".docx": b"PK\x03\x04",
    }
    if ext in magic_map:
        with open(path, "rb") as f:
            header = f.read(4)
        if not header.startswith(magic_map[ext]):
            logger.warning(f"File header mismatch for {path}: expected {magic_map[ext]!r}, got {header!r}")
            return False
    return True


def save_to_collected_data(
    src_path: str | Path,
    category: str,
    source: str = "",
    keep_original_name: bool = True,
) -> dict:
    _ensure_metadata()
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    if not validate_file_extension(src):
        record = _log_rejection(src, category, source, "Unsupported file extension")
        return {"status": "rejected", "reason": "Unsupported file extension", "record": record}

    if not validate_file_content(src):
        record = _log_rejection(src, category, source, "File content validation failed")
        return {"status": "rejected", "reason": "Content validation failed", "record": record}

    dest_dir = DATA_ROOT / category
    if not dest_dir.exists():
        logger.error(f"Category directory does not exist: {dest_dir}")
        return {"status": "error", "reason": f"Unknown category: {category}"}

    if keep_original_name:
        dest_name = src.name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_name = f"{src.stem}_{timestamp}{src.suffix}"

    dest_path = dest_dir / dest_name
    if dest_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_name = f"{src.stem}_{timestamp}{src.suffix}"
        dest_path = dest_dir / dest_name

    shutil.copy2(src, dest_path)
    logger.info(f"Saved: {src} -> {dest_path}")

    record = {
        "filename": dest_name,
        "category": category,
        "source": source,
        "original_path": str(src),
        "saved_path": str(dest_path),
        "file_size_bytes": dest_path.stat().st_size,
        "file_extension": src.suffix.lower(),
        "collected_at": datetime.now().isoformat(),
        "status": "accepted",
    }
    metadata = _load_metadata()
    metadata.append(record)
    _save_metadata(metadata)

    return {"status": "accepted", "record": record}


def _log_rejection(src_path: Path, category: str, source: str, reason: str) -> dict:
    dest = REJECTED_DIR / src_path.name
    if src_path.exists():
        shutil.copy2(src_path, dest)

    record = {
        "filename": src_path.name,
        "category": category,
        "source": source,
        "original_path": str(src_path),
        "file_extension": src_path.suffix.lower(),
        "rejection_reason": reason,
        "rejected_at": datetime.now().isoformat(),
        "status": "rejected",
    }
    metadata = _load_metadata()
    metadata.append(record)
    _save_metadata(metadata)
    logger.warning(f"Rejected: {src_path} - {reason}")

    return record


def get_metadata_summary() -> dict:
    metadata = _load_metadata()
    summary = {
        "total_files": len(metadata),
        "accepted": len([r for r in metadata if r["status"] == "accepted"]),
        "rejected": len([r for r in metadata if r["status"] == "rejected"]),
        "by_category": {},
    }
    for r in metadata:
        cat = r.get("category", "unknown")
        summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1
    return summary
