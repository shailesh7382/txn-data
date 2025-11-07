#!/usr/bin/env python3
"""
search_medical_pdfs.py

Recursively scan a folder for PDFs, detect those that contain
a medical theme (via keyword matching), log them,
and optionally extract all tables with Camelot.
"""

import argparse
import logging
from pathlib import Path

try:
    import pdfplumber
except ImportError as e:      # pragma: no cover
    raise SystemExit("pdfplumber is required. Install with pip install pdfplumber") from e

# Camelot is optional – the script will still run if it isn’t installed
try:
    import camelot
except ImportError:          # pragma: no cover
    camelot = None

# --------------------------------------------------------------------------- #
# 1. Logging --------------------------------------------------------------- #
def setup_logging(log_file: str) -> None:
    """Configure a simple console + file logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


# --------------------------------------------------------------------------- #
# 2. Medical keyword list --------------------------------------------------- #
MEDICAL_KEYWORDS = [
    # From your citations – feel free to add more
    "urine", "clinical", "diagnosis", "biochemistry",
    "blood", "hematology", "full body checkup",
    "treatment",
    "symptom", "patient", "pathology",
    # Domain‑specific terms you might want
    "osteomalacia", "malabsorption", "renal", "kidney",
    "hepatic", "glucose", "creatinine"
]

def find_medical_keywords(text: str):
    """Return a list of medical keywords that appear in the text (deduped, in original order)."""
    lower = text.lower()
    found = []
    for k in MEDICAL_KEYWORDS:
        if k in lower and k not in found:
            found.append(k)
    return found

def is_medical(text: str) -> bool:
    """Return True if any medical keyword appears in the text."""
    return bool(find_medical_keywords(text))


# --------------------------------------------------------------------------- #
# 3. PDF utilities ---------------------------------------------------------- #
def extract_text(pdf_path: Path) -> str:
    """Return the concatenated text of all pages in a PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as exc:      # pragma: no cover
        logging.warning(f"Failed to read {pdf_path}: {exc}")
        return ""


def extract_tables(pdf_path: Path, out_dir: Path) -> None:
    """Use Camelot to dump all tables as CSVs into out_dir."""
    if camelot is None:
        logging.error("Camelot not installed – skipping table extraction.")
        return
    try:
        tables = camelot.read_pdf(str(pdf_path), pages="all", flavor="stream")
        for i, tbl in enumerate(tables):
            out_file = out_dir / f"{pdf_path.stem}_table_{i+1}.csv"
            tbl.to_csv(out_file)
        logging.info(f"Extracted {len(tables)} tables from {pdf_path}")
    except Exception as exc:      # pragma: no cover
        logging.error(f"Error extracting tables from {pdf_path}: {exc}")


# --------------------------------------------------------------------------- #
# 4. Main logic ------------------------------------------------------------ #
def process_folder(root: Path, log_file: str, extract_tables_flag: bool) -> None:
    """Walk the folder tree, match PDFs and log / process them."""
    if not root.is_dir():
        logging.error(f"Root folder {root} does not exist.")
        return

    for pdf_path in root.rglob("*.pdf"):
        # removed per-file scanning/info logs to only report matches
        txt = extract_text(pdf_path)
        if not txt:
            continue

        matches = find_medical_keywords(txt)
        if matches:
            keywords_str = ", ".join(matches)
            # Log to the configured logger (console + file handler)
            logging.info(f"✅ Medical PDF found: {pdf_path} | keywords: {keywords_str}")
            # Append the path and keywords to the log file (one per line)
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"{pdf_path}\t{keywords_str}\n")

            if extract_tables_flag:
                tables_dir = pdf_path.parent / "tables"
                tables_dir.mkdir(exist_ok=True)
                extract_tables(pdf_path, tables_dir)
        # no debug/negative logs here so only matches are emitted


# --------------------------------------------------------------------------- #
# 5. CLI entry point ------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recursively find medical PDFs, log them, and optionally extract tables."
    )
    parser.add_argument("folder", help="Root folder to search")
    parser.add_argument(
        "--log",
        default="medical_pdfs.log",
        help="Path to the log file (default: medical_pdfs.log)",
    )
    parser.add_argument(
        "--extract-tables",
        action="store_true",
        help="Run Camelot on each matched PDF to dump tables as CSVs",
    )
    args = parser.parse_args()

    setup_logging(args.log)
    process_folder(Path(args.folder), args.log, args.extract_tables)


if __name__ == "__main__":
    main()
