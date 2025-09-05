import pdfplumber
import csv
import os
import glob

PDF_DIR = "generated-pdf"
CSV_FILE = "fx_transactions.csv"

def extract_table_from_pdf(pdf_file):
    all_rows = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                all_rows.extend(table)
    return all_rows

def write_csv(table, csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        for row in table:
            writer.writerow(row)

if __name__ == "__main__":
    all_tables = []
    seen_headers = set()
    header_row = None

    pdf_files = sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf")))
    for pdf_file in pdf_files:
        table = extract_table_from_pdf(pdf_file)
        for row in table:
            if not any(cell.strip() for cell in row):
                continue
            header_tuple = tuple(cell.strip().lower() for cell in row)
            if header_row is None:
                header_row = row
                all_tables.append(row)
                seen_headers.add(header_tuple)
            elif header_tuple == tuple(cell.strip().lower() for cell in header_row):
                continue  # skip duplicate header
            else:
                all_tables.append(row)
    write_csv(all_tables, CSV_FILE)
    print(f"CSV generated: {CSV_FILE}")

# pdfplumber is a strong choice for extracting tables from PDFs.
# Alternatives: camelot, tabula-py (require Java or work best with specific PDF types).
# For most text-based PDFs, pdfplumber is reliable and easy to use.
