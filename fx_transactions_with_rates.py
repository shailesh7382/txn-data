import pandas as pd
from clickhouse_driver import Client
from datetime import datetime, timedelta

# Read transactions
df = pd.read_csv("fx_transactions.csv")

# Normalize column names to lower for easier access
df.columns = [c.strip().lower() for c in df.columns]

# Connect to ClickHouse
client = Client(
    host='localhost',
    port=9000,
    user='default',
    password='default',
    database='default'
)

def get_ccypair(row):
    from_ccy = str(row['from ccy']).upper()
    to_ccy = str(row['to ccy']).upper()
    return from_ccy + to_ccy

df['bid_max'] = None
df['bid_min'] = None
df['ask_max'] = None
df['ask_min'] = None

for idx, row in df.iterrows():
    # Parse tradedatetime in format dd/mm/yy HH:MM:SS
    tradedatetime = row.get('tradedatetime') or row.get('trade datetime') or row.get('trade_datetime')
    if pd.notnull(tradedatetime):
        try:
            trade_time = datetime.strptime(tradedatetime, '%d/%m/%y %H:%M:%S')
        except Exception:
            continue  # skip if parsing fails
    else:
        continue  # skip if no time info

    ccypair = get_ccypair(row)
    start_time = trade_time - timedelta(seconds=30)
    end_time = trade_time

    query = f"""
    SELECT bids, asks
    FROM fx_price
    WHERE ccypair = '{ccypair}'
      AND timestamp >= toDateTime64('{start_time}', 9)
      AND timestamp < toDateTime64('{end_time}', 9)
    """

    try:
        result = client.execute(query)
    except Exception:
        continue

    bids_1 = []
    asks_1 = []
    for bids, asks in result:
        if isinstance(bids, list) and len(bids) > 1:
            bids_1.append(bids[1])
        if isinstance(asks, list) and len(asks) > 1:
            asks_1.append(asks[1])
    if bids_1:
        df.at[idx, 'bid_max'] = max(bids_1)
        df.at[idx, 'bid_min'] = min(bids_1)
    if asks_1:
        df.at[idx, 'ask_max'] = max(asks_1)
        df.at[idx, 'ask_min'] = min(asks_1)

df.to_csv("fx_transactions_with_rates.csv", index=False)
print("fx_transactions_with_rates.csv generated.")
