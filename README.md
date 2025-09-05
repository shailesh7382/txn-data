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


## clickhouse details 
docker run -d --name clickhouse-server \
-e CLICKHOUSE_DB=default \
-e CLICKHOUSE_USER=default \
-e CLICKHOUSE_PASSWORD=MyNewSecretPass \
-p 8123:8123 -p 9000:9000 clickhouse/clickhouse-server



http://localhost:8123/play

create a clickhouse db table called fx_price that contains timestamp in nanos, date, array of double for bids, array of double for asks and array of doubles for respective quantities and 
ccypair, and quoteId and name  


