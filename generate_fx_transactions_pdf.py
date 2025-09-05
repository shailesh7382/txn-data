import random
import os
from datetime import datetime, timedelta
from fpdf import FPDF

CURRENCIES = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'NZD', 'CHF', 'NOK', 'HKD']
N_TRANSACTIONS = 100
USD_ONLY = True  # Set to True to generate only USD pairs

def random_date_on_22_july_2025():
    base_date = datetime(2025, 7, 22)
    # Random time during the day
    seconds = random.randint(0, 9000) # 0 to 2.5 hours (9000 seconds) from midnight to 2:30 AM for full overlap with fx_price data
    return base_date + timedelta(seconds=seconds)

def generate_transactions(n):
    transactions = []
    for i in range(n):
        dt = random_date_on_22_july_2025()
        tradedatetime = dt.strftime('%d/%m/%y %H:%M:%S')
        if USD_ONLY:
            # Pick one side as USD, the other as a non-USD currency
            non_usd_currencies = [c for c in CURRENCIES if c != 'USD']
            if random.choice([True, False]):
                from_cur = 'USD'
                to_cur = random.choice(non_usd_currencies)
            else:
                from_cur = random.choice(non_usd_currencies)
                to_cur = 'USD'
        else:
            from_cur, to_cur = random.sample(CURRENCIES, 2)
        buy_sell = random.choice(['Buy', 'Sell'])
        exchange_rate = round(random.uniform(0.5, 1.5), 4)
        if buy_sell == 'Buy':
            from_amt = round(random.uniform(100, 10000), 2)
            to_amt = round(from_amt * exchange_rate, 2)
        else:
            to_amt = round(random.uniform(100, 10000), 2)
            from_amt = round(to_amt * exchange_rate, 2)
        txn = {
            'tradedatetime': tradedatetime,
            'buy_sell': buy_sell,
            'from_ccy': from_cur,
            'to_ccy': to_cur,
            'from_amt': from_amt,
            'to_amt': to_amt,
            'exchange_rate': exchange_rate,
            'txn_number': f'TXN{i+1:04d}',
            'account': f"ACCT{random.randint(100000, 999999)}"
        }
        transactions.append(txn)
    return transactions

def create_pdf(transactions, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, "FX Transactions Report", align='C', ln=1)
    pdf.ln(5)
    headers = ['TradeDateTime', 'Buy/Sell', 'From CCY', 'To CCY', 'From Amt', 'To Amt', 'Exchange Rate', 'Txn Number', 'Account']
    col_widths = [32, 18, 18, 18, 28, 28, 28, 28, 28]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align='C')
    pdf.ln()
    for txn in transactions:
        pdf.cell(col_widths[0], 8, txn['tradedatetime'], border=1)
        pdf.cell(col_widths[1], 8, txn['buy_sell'], border=1)
        pdf.cell(col_widths[2], 8, txn['from_ccy'], border=1)
        pdf.cell(col_widths[3], 8, txn['to_ccy'], border=1)
        pdf.cell(col_widths[4], 8, f"{txn['from_amt']:.2f}", border=1, align='R')
        pdf.cell(col_widths[5], 8, f"{txn['to_amt']:.2f}", border=1, align='R')
        pdf.cell(col_widths[6], 8, f"{txn['exchange_rate']:.4f}", border=1, align='R')
        pdf.cell(col_widths[7], 8, txn['txn_number'], border=1)
        pdf.cell(col_widths[8], 8, txn['account'], border=1)
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
