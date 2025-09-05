# FX Transactions PDF/CSV Utility

## Setup

1. Create and activate a virtual environment (optional but recommended):

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Generate PDF with FX Transactions

```sh
python generate_fx_transactions_pdf.py
```

This will create `fx_transactions.pdf` in the current directory.

### Convert PDF to CSV

```sh
python pdf_to_csv_fx_transactions.py
```

This will create `fx_transactions.csv` in the current directory.

## Notes

- The PDF contains 100 randomly generated FX transactions.
- The CSV is extracted from the PDF and contains the same data.

