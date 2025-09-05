from clickhouse_driver import Client

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
LIMIT 10
"""

result = client.execute(query)
for row in result:
    print(row)
