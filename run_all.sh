#!/bin/bash
set -e

echo "Cleaning up previous generated files..."
rm -f fx_transactions.csv fx_transactions_with_rates.csv
rm -rf generated-pdf
mkdir -p generated-pdf
echo "Cleanup complete."

echo "Generating FX transactions PDF(s)..."
python generate_fx_transactions_pdf.py
echo "PDF generation complete."

echo "Extracting transactions from PDF(s) to CSV..."
python pdf_to_csv_fx_transactions.py
echo "CSV extraction complete."

echo "Enriching transactions with FX rates from ClickHouse..."
python fx_transactions_with_rates.py
echo "FX rates enrichment complete."

echo "All steps finished successfully."
