#!/usr/bin/env python3
"""Prepare paper source files for OpenClaw, Codex, or Claude Code workflows.

This helper adapts the pure-stdlib arXiv search/download pattern used by ARIS
(`tools/arxiv_fetch.py`) and adds project-specific source preparation:

- normalize arXiv IDs / URLs
- fetch arXiv metadata
- create a timestamped run directory under `paper-analysis/`
- download the PDF into `<analysis-dir>/sources/`
- extract text when `pypdf`, `PyPDF2`, or `pdftotext` is available
- write source manifests that an OpenClaw agent can read before generating the
  seven analysis documents
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ATOM_NS = "http://www.w3.org/2005/Atom"
ARXIV_API_BASE = "http://export.arxiv.org/api/query"
USER_AGENT = "paper-praser-agent/0.1 (+https://github.com/DebugTheWorld233/paper-praser-agent)"
MIN_PDF_BYTES = 10_240
MAX_SLUG_LENGTH = 96
NEW_STYLE_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
OLD_STYLE_ID_RE = re.compile(r"^[A-Za-z.-]+/\d{7}(v\d+)?$")


@dataclass
class PreparedSource:
    analysis_dir: str
    source: str
    source_type: str
    pdf_path: str | None
    text_path: str | None
    metadata_path: str
    extraction_status: str


def normalize_arxiv_id(value: str) -> str:
    """Strip URL/version noise and return a clean arXiv ID."""
    value = value.strip()
    if "/abs/" in value:
        value = value.split("/abs/", 1)[1]
    if "/pdf/" in value:
        value = value.split("/pdf/", 1)[1]
    if value.endswith(".pdf"):
        value = value[:-4]
    if value.startswith("arxiv:"):
        value = value[6:]
    if value.startswith("id:"):
        value = value[3:]
    if "?" in value:
        value = value.split("?", 1)[0]
    if "#" in value:
        value = value.split("#", 1)[0]
    if "v" in value.split(".")[-1]:
        value = value.rsplit("v", 1)[0]
    return value.strip("/")


def looks_like_arxiv_id(value: str) -> bool:
    value = normalize_arxiv_id(value)
    return bool(NEW_STYLE_ID_RE.match(value) or OLD_STYLE_ID_RE.match(value))


def detect_source_type(source: str) -> str:
    value = source.strip()
    lower = value.lower()
    if looks_like_arxiv_id(value) or "arxiv.org/abs/" in lower or "arxiv.org/pdf/" in lower:
        return "arxiv"
    if lower.startswith("http://") or lower.startswith("https://"):
        if lower.endswith(".pdf") or ".pdf?" in lower:
            return "pdf_url"
        return "url"
    if Path(value).exists():
        return "local_pdf" if lower.endswith(".pdf") else "local_file"
    return "unknown"


def slugify(value: str, *, fallback: str = "paper") -> str:
    """Return a filesystem-friendly ASCII slug."""
    value = value.strip().lower()
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-._")
    return value[:MAX_SLUG_LENGTH].strip("-._") or fallback


def build_source_slug(source: str, source_type: str, metadata: dict) -> str:
    arxiv_id = metadata.get("id")
    authors = metadata.get("authors") or []
    if arxiv_id and authors:
        return slugify(f"{authors[0]}-{arxiv_id}")
    if arxiv_id:
        return slugify(arxiv_id)
    if source_type == "local_pdf":
        return slugify(Path(source).stem)
    if source_type == "pdf_url":
        filename = Path(urllib.parse.urlparse(source).path).stem
        return slugify(filename)
    if source_type == "url":
        parsed = urllib.parse.urlparse(source)
        return slugify(f"{parsed.netloc}-{parsed.path}")
    return slugify(source)


def unique_child_dir(root: Path, slug: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = root / f"{timestamp}_{slug}"
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = root / f"{base.name}-{suffix}"
        suffix += 1
    return candidate


def arxiv_api_url(arxiv_id: str) -> str:
    params = {"id_list": normalize_arxiv_id(arxiv_id)}
    return f"{ARXIV_API_BASE}?{urllib.parse.urlencode(params)}"


def fetch_arxiv_metadata(arxiv_id: str) -> dict:
    req = urllib.request.Request(arxiv_api_url(arxiv_id), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    entries = root.findall(f"{{{ATOM_NS}}}entry")
    if not entries:
        raise ValueError(f"No arXiv metadata found for {arxiv_id}")
    entry = entries[0]
    raw_id = entry.findtext(f"{{{ATOM_NS}}}id", "")
    clean_id = normalize_arxiv_id(raw_id)
    return {
        "id": clean_id,
        "title": (entry.findtext(f"{{{ATOM_NS}}}title", "") or "").strip().replace("\n", " "),
        "authors": [
            author.findtext(f"{{{ATOM_NS}}}name", "")
            for author in entry.findall(f"{{{ATOM_NS}}}author")
        ],
        "abstract": (entry.findtext(f"{{{ATOM_NS}}}summary", "") or "").strip().replace("\n", " "),
        "published": (entry.findtext(f"{{{ATOM_NS}}}published", "") or "")[:10],
        "updated": (entry.findtext(f"{{{ATOM_NS}}}updated", "") or "")[:10],
        "categories": [
            category.get("term", "")
            for category in entry.findall(f"{{{ATOM_NS}}}category")
            if category.get("term")
        ],
        "abs_url": f"https://arxiv.org/abs/{clean_id}",
        "pdf_url": f"https://arxiv.org/pdf/{clean_id}.pdf",
    }


def download_url(url: str, dest: Path, *, min_bytes: int = MIN_PDF_BYTES) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size >= min_bytes:
        return {"path": str(dest), "size_kb": dest.stat().st_size // 1024, "skipped": True}

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt == 1:
                time.sleep(5)
                continue
            raise
    else:
        raise RuntimeError(f"Failed to download {url}")

    if len(data) < min_bytes:
        raise ValueError(f"Downloaded file is only {len(data)} bytes; likely not a valid PDF")

    dest.write_bytes(data)
    return {"path": str(dest), "size_kb": len(data) // 1024, "skipped": False}


def import_pdf_reader():
    try:
        from pypdf import PdfReader  # type: ignore

        return PdfReader, "pypdf"
    except Exception:
        pass
    try:
        from PyPDF2 import PdfReader  # type: ignore

        return PdfReader, "PyPDF2"
    except Exception:
        return None, None


def extract_with_python(pdf_path: Path) -> tuple[str | None, str | None]:
    reader_cls, backend = import_pdf_reader()
    if reader_cls is None:
        return None, None
    reader = reader_cls(str(pdf_path))
    chunks: list[str] = []
    for page_index, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:
            page_text = f"[PAGE {page_index} EXTRACTION_ERROR: {exc}]"
        chunks.append(f"\n\n## Page {page_index}\n\n{page_text.strip()}")
    return "\n".join(chunks).strip(), backend


def extract_with_pdftotext(pdf_path: Path) -> tuple[str | None, str | None]:
    exe = shutil.which("pdftotext")
    if not exe:
        return None, None
    completed = subprocess.run(
        [exe, "-layout", str(pdf_path), "-"],
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        return None, f"pdftotext failed: {completed.stderr.strip()}"
    return completed.stdout.strip(), "pdftotext"


def extract_pdf_text(pdf_path: Path, text_path: Path) -> dict:
    text_path.parent.mkdir(parents=True, exist_ok=True)

    text, backend = extract_with_python(pdf_path)
    if text:
        text_path.write_text(text + "\n", encoding="utf-8")
        return {"status": "ok", "backend": backend, "path": str(text_path), "chars": len(text)}

    text, backend = extract_with_pdftotext(pdf_path)
    if text:
        text_path.write_text(text + "\n", encoding="utf-8")
        return {"status": "ok", "backend": backend, "path": str(text_path), "chars": len(text)}

    blocker = text_path.with_name("EXTRACTION_BLOCKED.md")
    blocker.write_text(
        "# PDF 文本抽取失败\n\n"
        "未检测到可用的 Python PDF 解析库或 `pdftotext`。\n\n"
        "可选解决方式：\n\n"
        "1. 安装 `pypdf`：`python -m pip install pypdf`\n"
        "2. 安装 Poppler，并确保 `pdftotext` 在 PATH 中。\n"
        "3. 让 OpenClaw 直接读取 PDF，或人工提供论文文本。\n",
        encoding="utf-8",
    )
    return {"status": "blocked", "backend": None, "path": None, "blocker": str(blocker)}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(source: str, out_dir: Path, *, flat: bool = False) -> PreparedSource:
    source_type = detect_source_type(source)
    metadata: dict = {"input": source, "source_type": source_type}
    pdf_path: Path | None = None

    if source_type == "arxiv":
        arxiv_id = normalize_arxiv_id(source)
        metadata.update(fetch_arxiv_metadata(arxiv_id))

    analysis_dir = out_dir if flat else unique_child_dir(out_dir, build_source_slug(source, source_type, metadata))
    source_dir = analysis_dir / "sources"
    source_dir.mkdir(parents=True, exist_ok=True)
    metadata["analysis_dir"] = str(analysis_dir)

    if source_type == "arxiv":
        safe_id = metadata["id"].replace("/", "_")
        pdf_path = source_dir / f"{safe_id}.pdf"
        metadata["download"] = download_url(metadata["pdf_url"], pdf_path)
    elif source_type == "pdf_url":
        filename = Path(urllib.parse.urlparse(source).path).name or "paper.pdf"
        pdf_path = source_dir / filename
        metadata["pdf_url"] = source
        metadata["download"] = download_url(source, pdf_path)
    elif source_type == "local_pdf":
        local = Path(source).resolve()
        pdf_path = source_dir / local.name
        if local != pdf_path.resolve():
            shutil.copy2(local, pdf_path)
        metadata["local_source"] = str(local)
        metadata["download"] = {"path": str(pdf_path), "size_kb": pdf_path.stat().st_size // 1024, "skipped": True}
    else:
        metadata["warning"] = (
            "Source is not an arXiv ID/URL or local PDF. OpenClaw should read it directly "
            "or the user should provide a PDF."
        )

    text_path: Path | None = None
    extraction = {"status": "not_attempted", "reason": "no_pdf"}
    if pdf_path is not None:
        text_path = source_dir / "paper_text.md"
        extraction = extract_pdf_text(pdf_path, text_path)

    metadata["pdf_path"] = str(pdf_path) if pdf_path else None
    metadata["text_path"] = str(text_path) if extraction.get("path") else None
    metadata["text_extraction"] = extraction

    metadata_path = source_dir / "source_metadata.json"
    write_json(metadata_path, metadata)

    return PreparedSource(
        analysis_dir=str(analysis_dir),
        source=source,
        source_type=source_type,
        pdf_path=str(pdf_path) if pdf_path else None,
        text_path=str(text_path) if extraction.get("path") else None,
        metadata_path=str(metadata_path),
        extraction_status=extraction["status"],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare paper source files for paper-solution-agent.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="Download/copy a paper and extract text when possible")
    prepare_parser.add_argument("source", help="arXiv ID/URL, direct PDF URL, or local PDF path")
    prepare_parser.add_argument(
        "--out",
        default="paper-analysis",
        help=(
            "Analysis root directory (default: paper-analysis). By default the command creates "
            "a timestamped child directory under this root."
        ),
    )
    prepare_parser.add_argument(
        "--flat",
        action="store_true",
        help="Use --out exactly, preserving the legacy flat paper-analysis/sources layout.",
    )

    metadata_parser = subparsers.add_parser("metadata", help="Fetch arXiv metadata only")
    metadata_parser.add_argument("arxiv_id", help="arXiv ID or URL")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "prepare":
        result = prepare(args.source, Path(args.out), flat=args.flat)
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
        return 0
    if args.command == "metadata":
        print(json.dumps(fetch_arxiv_metadata(args.arxiv_id), ensure_ascii=False, indent=2))
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
