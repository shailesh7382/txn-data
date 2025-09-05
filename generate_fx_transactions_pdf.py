import random
import os
from datetime import datetime, timedelta
from fpdf import FPDF, XPos, YPos

CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'INR']
N_TRANSACTIONS = 100

def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )

def generate_transactions(n):
    transactions = []
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    for i in range(n):
        dt = random_date(start_date, end_date)
        datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        from_cur, to_cur = random.sample(CURRENCIES, 2)
        amount = round(random.uniform(100, 10000), 2)
        rate = round(random.uniform(0.5, 1.5), 4)
        account = f"ACCT{random.randint(100000, 999999)}"
        txn = {
            'id': f'TXN{i+1:04d}',
            'datetime': datetime_str,
            'account': account,
            'from': from_cur,
            'to': to_cur,
            'dealt_ccy': from_cur,
            'amount': amount,
            'rate': rate,
        }
        transactions.append(txn)
    return transactions

def create_pdf(transactions, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, "FX Transactions Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(5)
    headers = ['ID', 'DateTime', 'Account', 'From', 'To', 'Dealt CCY', 'Amount', 'Rate']
    col_widths = [20, 38, 28, 16, 16, 22, 24, 16]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align='C')
    pdf.ln()
    for txn in transactions:
        pdf.cell(col_widths[0], 8, txn['id'], border=1)
        pdf.cell(col_widths[1], 8, txn['datetime'], border=1)
        pdf.cell(col_widths[2], 8, txn['account'], border=1)
        pdf.cell(col_widths[3], 8, txn['from'], border=1)
        pdf.cell(col_widths[4], 8, txn['to'], border=1)
        pdf.cell(col_widths[5], 8, txn['dealt_ccy'], border=1)
        pdf.cell(col_widths[6], 8, f"{txn['amount']:.2f}", border=1, align='R')
        pdf.cell(col_widths[7], 8, f"{txn['rate']:.4f}", border=1, align='R')
        pdf.ln()
    pdf.output(filename)

# fpdf is a suitable choice for generating simple PDF tables.
# For more complex layouts, consider reportlab, but for this use case fpdf is efficient and easy to use.

if __name__ == "__main__":
    output_dir = "generated-pdf"
    os.makedirs(output_dir, exist_ok=True)
    for i in range(3):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rand_suffix = random.randint(1000, 9999)
        fname = os.path.join(
            output_dir,
            f"fx_transactions_{timestamp}_{rand_suffix}.pdf"
        )
        transactions = generate_transactions(N_TRANSACTIONS)
        create_pdf(transactions, fname)
        print(f"PDF generated: {fname}")
