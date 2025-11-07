#!/usr/bin/env python3
"""
pdf_reader.py – A robust, self‑contained PDF reader.

Usage:
    python pdf_reader.py <path_or_url> [--output OUTDIR] [--verbose]

Dependencies (install via pip):
    pip install PyPDF2 pdfplumber pdfminer.six tqdm requests
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple

# -------------------------------------------------
# 1. Import libraries – fall back to stub if missing
# -------------------------------------------------
try:
    import PyPDF2
except ImportError:  # pragma: no cover
    print("Missing PyPDF2 – install with `pip install PyPDF2`")
    sys.exit(1)

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    print("Missing pdfplumber – install with `pip install pdfplumber`")
    sys.exit(1)

try:
    from pdfminer.high_level import extract_text as pm_extract_text
except ImportError:  # pragma: no cover
    print("Missing pdfminer.six – install with `pip install pdfminer.six`")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    print("Missing tqdm – install with `pip install tqdm`")
    sys.exit(1)

import requests
from urllib.parse import urlparse

# -------------------------------------------------
# 2. Helpers
# -------------------------------------------------
def download_pdf(url: str, tmp_dir: Path) -> Path:
    """Download a PDF from a URL to a temporary directory."""
    parsed = urlparse(url)
    if not parsed.scheme.startswith("http"):
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")

    local_path = tmp_dir / Path(parsed.path).name
    if not local_path.suffix.lower() == ".pdf":
        local_path = local_path.with_suffix(".pdf")

    r = requests.get(url, stream=True, timeout=15)
    r.raise_for_status()
    with open(local_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return local_path

def extract_with_pypdf2(pdf_path: Path) -> Tuple[List[str], dict]:
    """Extract text and metadata using PyPDF2."""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        page_texts = [p.extract_text() or "" for p in reader.pages]
        meta = {
            "title": reader.metadata.title,
            "author": reader.metadata.author,
            "creator": reader.metadata.creator,
            "producer": reader.metadata.producer,
            "subject": reader.metadata.subject,
        }
    return page_texts, meta

def extract_with_pdfplumber(pdf_path: Path) -> Tuple[List[str], dict]:
    """Extract text using pdfplumber (handles scanned PDFs better)."""
    page_texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            page_texts.append(pg.extract_text() or "")
    # pdfplumber does not expose metadata directly
    meta = {}
    return page_texts, meta

def extract_with_pdfminer(pdf_path: Path) -> Tuple[List[str], dict]:
    """Extract full‑text with pdfminer (good for complex layouts)."""
    text = pm_extract_text(str(pdf_path))
    # pdfminer gives the whole doc as one string – split on page breaks
    page_texts = text.split("\f")  # form feed often used as page delimiter
    meta = {}
    return page_texts, meta

def best_extraction(pdf_path: Path, verbose: bool = False) -> Tuple[List[str], dict]:
    """Try all back‑ends, return the best result."""
    methods = [
        ("PyPDF2", extract_with_pypdf2),
        ("pdfplumber", extract_with_pdfplumber),
        ("pdfminer.six", extract_with_pdfminer),
    ]

    best_text = []
    best_meta = {}
    for name, func in methods:
        if verbose:
            print(f"[{name}] extracting…")
        try:
            text, meta = func(pdf_path)
            # Prefer the one that returns more non‑empty pages
            if len([t for t in text if t.strip()]) > len(best_text):
                best_text, best_meta = text, meta
        except Exception as e:
            if verbose:
                print(f"  → {name} failed: {e}")

    return best_text, best_meta

def write_output(
        pdf_path: Path,
        page_texts: List[str],
        meta: dict,
        out_dir: Path,
        verbose: bool = False,
):
    """Write plain‑text and JSON dump to out_dir."""
    base_name = pdf_path.stem
    txt_out = out_dir / f"{base_name}.txt"
    json_out = out_dir / f"{base_name}_pages.json"

    # Plain‑text
    with open(txt_out, "w", encoding="utf-8") as f:
        for i, txt in enumerate(page_texts, start=1):
            f.write(f"--- Page {i} ---\n")
            f.write(txt.strip() + "\n\n")

    # JSON (page‑by‑page)
    pages_json = [{"page": i + 1, "text": txt} for i, txt in enumerate(page_texts)]
    dump = {
        "metadata": meta,
        "pages": pages_json,
    }
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(dump, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"✅ Text written to: {txt_out}")
        print(f"✅ JSON written to: {json_out}")

# -------------------------------------------------
# 3. CLI
# -------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Extract PDF text with multiple back‑ends.")
    parser.add_argument("source", help="Local file path or HTTP(S) URL to a PDF.")
    parser.add_argument("--output", "-o", default=".", help="Directory to write results (default: current dir).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print progress information.")
    args = parser.parse_args()

    out_dir = Path(args.output).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Resolve source to a local file
    if args.source.lower().startswith(("http://", "https://")):
        tmp_dir = Path.cwd() / ".pdf_reader_tmp"
        tmp_dir.mkdir(exist_ok=True)
        pdf_path = download_pdf(args.source, tmp_dir)
    else:
        pdf_path = Path(args.source).expanduser().resolve()
        if not pdf_path.is_file():
            print(f"❌ File does not exist: {pdf_path}")
            sys.exit(1)

    if args.verbose:
        print(f"[INFO] Processing: {pdf_path}")

    page_texts, meta = best_extraction(pdf_path, verbose=args.verbose)
    write_output(pdf_path, page_texts, meta, out_dir, verbose=args.verbose)

if __name__ == "__main__":
    main()
