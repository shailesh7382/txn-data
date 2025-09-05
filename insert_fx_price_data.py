from clickhouse_driver import Client
from datetime import datetime, timedelta
import random

client = Client(
    host='localhost',
    port=9000,
    user='default',
    password='default',
    database='default'
)

ccypairs = [
    'EURUSD', 'USDJPY', 'GBPUSD', 'AUDUSD', 'USDCAD',
    'NZDUSD', 'USDCHF', 'USDSEK', 'USDMXN', 'USDNOK', 'USDHKD', 'USDTRY'
]
qtys = [1_000_000, 5_000_000, 10_000_000]
bids_base = [
    1.10, 110.0, 1.30, 0.75, 1.25,
    0.70, 0.90, 10.0, 18.0, 9.0, 7.8, 32.0
]
asks_base = [
    1.11, 110.2, 1.31, 0.76, 1.26,
    0.71, 0.91, 10.1, 18.1, 9.1, 7.9, 32.2
]
date_str = '2025-07-22'
date_obj = datetime.strptime(date_str, '%Y-%m-%d')
date_only = date_obj.date()  # Use as date object

start_time = datetime(2025, 7, 22, 1, 0, 0)
end_time = datetime(2025, 7, 22, 2, 0, 0)
total_seconds = int((end_time - start_time).total_seconds())

rows = []
for idx, ccypair in enumerate(ccypairs):
    for i in range(total_seconds):  # 1-second intervals between 1am and 2am
        ts = start_time + timedelta(seconds=i)
        bids = [round(bids_base[idx] - 0.0001 * j - random.uniform(0, 0.0002), 6) for j in range(3)]
        asks = [round(asks_base[idx] + 0.0001 * j + random.uniform(0, 0.0002), 6) for j in range(3)]
        row = (
            ts,              # DateTime64(9)
            date_only,       # Date as date object
            bids,
            asks,
            qtys,
            ccypair,
            f"Q{random.randint(10000,99999)}",
            f"Source{idx+1}"
        )
        rows.append(row)

insert_query = """
INSERT INTO fx_price (
    timestamp, date, bids, asks, qtys, ccypair, quoteId, name
) VALUES
"""

client.execute(
    insert_query,
    rows
)

print(f"Inserted {len(rows)} rows into fx_price for {date_str} between 1am and 2am with 1-second intervals.")
