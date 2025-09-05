from clickhouse_driver import Client
import pandas as pd

# Connect to ClickHouse server (update host, user, password as needed)
client = Client(
    host='localhost',
    port=9000,
    user='default',
    password='default',
    database='default'
)

# Fetch latest EURUSD FX prices from fx_price table
query = """
SELECT
    timestamp,
    date,
    bids,
    asks,
    qtys,
    ccypair,
    quoteId,
    name
FROM fx_price
WHERE ccypair = 'EURUSD'
ORDER BY timestamp DESC
"""

result = client.execute(query)
columns = ['timestamp', 'date', 'bids', 'asks', 'qtys', 'ccypair', 'quoteId', 'name']
df = pd.DataFrame(result, columns=columns)
df.set_index('timestamp', inplace=True)
print(df)
