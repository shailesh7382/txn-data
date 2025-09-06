import pandas as pd
from clickhouse_driver import Client
from datetime import datetime, timedelta

print("Reading fx_transactions.csv...")
df = pd.read_csv("fx_transactions.csv")
print(f"Loaded {len(df)} transactions.")

# Normalize column names to lower for easier access
df.columns = [c.strip().lower() for c in df.columns]

print("Connecting to ClickHouse...")
client = Client(
    host='localhost',
    port=9000,
    user='default',
    password='default',
    database='default'
)
print("Connected to ClickHouse.")

USD = "USD"

def get_ccypair(row):
    from_ccy = str(row['from ccy']).upper()
    to_ccy = str(row['to ccy']).upper()
    return from_ccy + to_ccy, to_ccy + from_ccy, from_ccy, to_ccy

def fetch_fx_rows(ccypair, start_time, end_time):
    query = f"""
    SELECT timestamp, bids, asks
    FROM fx_price
    WHERE ccypair = '{ccypair}'
      AND timestamp >= toDateTime64('{start_time}', 9)
      AND timestamp < toDateTime64('{end_time}', 9)
    ORDER BY timestamp
    """
    print(f"Querying fx_price for ccypair={ccypair} from {start_time} to {end_time}...")
    rows = client.execute(query)
    print(f"Found {len(rows)} rows for {ccypair}.")
    return rows

def safe_get(arr, idx):
    return arr[idx] if isinstance(arr, list) and len(arr) > idx else None

df['bid_max'] = None
df['bid_min'] = None
df['ask_max'] = None
df['ask_min'] = None
df['ccypair_used'] = None
df['reciprocal'] = False
df['cross_used'] = None

# Add a column to indicate if bid price was used for transaction evaluation
df['used_bid'] = None

def determine_used_bid(buy_sell, from_ccy, to_ccy, used_ccypair, reciprocal):
    """
    Determines if bid or ask is used for the transaction, considering the direction and the standard pair.
    Returns True if bid is used, False if ask is used, None if undetermined.
    """
    if not buy_sell:
        return None
    buy_sell = buy_sell.strip().lower()
    # Standardize the pair direction to match fx_price convention
    # used_ccypair is the pair as found in fx_price (e.g., USDSGD)
    # reciprocal is True if the transaction direction is opposite to the fx_price pair
    if used_ccypair is None:
        return None  # For cross pairs, skip (or handle separately if needed)
    # If reciprocal, invert the logic
    if reciprocal:
        # Transaction is in the reverse direction of the fx_price pair
        if buy_sell == 'buy':
            return True   # Buy (reverse) uses bid
        elif buy_sell == 'sell':
            return False  # Sell (reverse) uses ask
    else:
        # Transaction matches fx_price pair direction
        if buy_sell == 'buy':
            return False  # Buy uses ask
        elif buy_sell == 'sell':
            return True   # Sell uses bid
    return None

print("Processing transactions and enriching with FX rates...")
for idx, row in df.iterrows():
    print(f"\nProcessing transaction {idx+1}/{len(df)}...")
    tradedatetime = row.get('tradedatetime') or row.get('trade datetime') or row.get('trade_datetime')
    if pd.notnull(tradedatetime):
        try:
            trade_time = datetime.strptime(tradedatetime, '%d/%m/%y %H:%M:%S')
            print(f"Parsed trade time: {trade_time}")
        except Exception as e:
            print(f"Failed to parse tradedatetime '{tradedatetime}': {e}. Skipping transaction.")
            continue
    else:
        print("No tradedatetime found. Skipping transaction.")
        continue

    ccypair, ccypair_rev, from_ccy, to_ccy = get_ccypair(row)
    start_time = trade_time - timedelta(seconds=30)
    end_time = trade_time

    # Direct USD pair
    if USD in [from_ccy, to_ccy]:
        reciprocal = False
        used_ccypair = None
        print(f"Transaction is a USD pair: {from_ccy}/{to_ccy}")
        # Try direct
        result = fetch_fx_rows(ccypair, start_time, end_time)
        if not result:
            print(f"No direct match for {ccypair}, trying reverse {ccypair_rev}...")
            # Try reverse
            result = fetch_fx_rows(ccypair_rev, start_time, end_time)
            reciprocal = True
            used_ccypair = ccypair_rev
        else:
            used_ccypair = ccypair

        bids_1 = []
        asks_1 = []
        for _, bids, asks in result:
            b = safe_get(bids, 1)
            a = safe_get(asks, 1)
            if not reciprocal:
                if b and a and b != 0 and a != 0:
                    bids_1.append(b)
                    asks_1.append(a)
            else:
                if b and a and b != 0 and a != 0:
                    bids_1.append(1 / a)
                    asks_1.append(1 / b)
        print(f"Collected {len(bids_1)} valid bids and {len(asks_1)} valid asks for USD pair.")
        if bids_1:
            df.at[idx, 'bid_max'] = max(bids_1)
            df.at[idx, 'bid_min'] = min(bids_1)
        if asks_1:
            df.at[idx, 'ask_max'] = max(asks_1)
            df.at[idx, 'ask_min'] = min(asks_1)
        df.at[idx, 'ccypair_used'] = used_ccypair
        df.at[idx, 'reciprocal'] = reciprocal
        df.at[idx, 'cross_used'] = None

        # Use new logic for bid/ask determination
        buy_sell = (row.get('buy/sell') or row.get('buy_sell') or '')
        used_bid = determine_used_bid(buy_sell, from_ccy, to_ccy, used_ccypair, reciprocal)
        df.at[idx, 'used_bid'] = used_bid
        continue

    # Cross pair: neither from_ccy nor to_ccy is USD
    print(f"Transaction is a cross pair: {from_ccy}/{to_ccy}. Calculating cross rate using USD legs.")
    xusd = from_ccy + USD
    usdx = USD + from_ccy
    usdy = USD + to_ccy
    yusd = to_ccy + USD

    leg_xusd = fetch_fx_rows(xusd, start_time, end_time)
    leg_usdx = fetch_fx_rows(usdx, start_time, end_time)
    leg_usdy = fetch_fx_rows(usdy, start_time, end_time)
    leg_yusd = fetch_fx_rows(yusd, start_time, end_time)

    cross_bids = []
    cross_asks = []
    cross_used = None

    # 1. X/USD and USD/Y (e.g., EURUSD * USDJPY)
    if leg_xusd and leg_usdy:
        print(f"Using {xusd} * {usdy} for cross calculation.")
        min_len = min(len(leg_xusd), len(leg_usdy))
        for i in range(min_len):
            _, bids1, asks1 = leg_xusd[i]
            _, bids2, asks2 = leg_usdy[i]
            b1 = safe_get(bids1, 1)
            a1 = safe_get(asks1, 1)
            b2 = safe_get(bids2, 1)
            a2 = safe_get(asks2, 1)
            if b1 and b2 and a1 and a2 and b1 != 0 and b2 != 0 and a1 != 0 and a2 != 0:
                cross_bids.append(b1 * b2)
                cross_asks.append(a1 * a2)
        cross_used = f"{xusd} * {usdy}"

    # 2. X/USD and Y/USD (e.g., EURUSD / USDJPY)
    elif leg_xusd and leg_yusd:
        print(f"Using {xusd} / {yusd} for cross calculation.")
        min_len = min(len(leg_xusd), len(leg_yusd))
        for i in range(min_len):
            _, bids1, asks1 = leg_xusd[i]
            _, bids2, asks2 = leg_yusd[i]
            b1 = safe_get(bids1, 1)
            a1 = safe_get(asks1, 1)
            b2 = safe_get(bids2, 1)
            a2 = safe_get(asks2, 1)
            # cross_bid = bid(X/USD) / ask(Y/USD)
            # cross_ask = ask(X/USD) / bid(Y/USD)
            if b1 and a2 and a1 and b2 and b1 != 0 and a2 != 0 and a1 != 0 and b2 != 0:
                cross_bids.append(b1 / a2)
                cross_asks.append(a1 / b2)
        cross_used = f"{xusd} / {yusd}"

    # 3. USD/X and USD/Y (e.g., 1/USDEUR * USDJPY)
    elif leg_usdx and leg_usdy:
        print(f"Using 1/{usdx} * {usdy} for cross calculation.")
        min_len = min(len(leg_usdx), len(leg_usdy))
        for i in range(min_len):
            _, bids1, asks1 = leg_usdx[i]
            _, bids2, asks2 = leg_usdy[i]
            b1 = safe_get(bids1, 1)
            a1 = safe_get(asks1, 1)
            b2 = safe_get(bids2, 1)
            a2 = safe_get(asks2, 1)
            # cross_bid = (1/ask(USD/X)) * bid(USD/Y)
            # cross_ask = (1/bid(USD/X)) * ask(USD/Y)
            if a1 and b2 and b1 and a2 and a1 != 0 and b2 != 0 and b1 != 0 and a2 != 0:
                cross_bids.append((1 / a1) * b2)
                cross_asks.append((1 / b1) * a2)
        cross_used = f"1/{usdx} * {usdy}"

    # 4. USD/X and Y/USD (e.g., 1/USDEUR / USDJPY)
    elif leg_usdx and leg_yusd:
        print(f"Using 1/{usdx} / {yusd} for cross calculation.")
        min_len = min(len(leg_usdx), len(leg_yusd))
        for i in range(min_len):
            _, bids1, asks1 = leg_usdx[i]
            _, bids2, asks2 = leg_yusd[i]
            b1 = safe_get(bids1, 1)
            a1 = safe_get(asks1, 1)
            b2 = safe_get(bids2, 1)
            a2 = safe_get(asks2, 1)
            # cross_bid = (1/ask(USD/X)) / ask(Y/USD)
            # cross_ask = (1/bid(USD/X)) / bid(Y/USD)
            if a1 and a2 and b1 and b2 and a1 != 0 and a2 != 0 and b1 != 0 and b2 != 0:
                cross_bids.append((1 / a1) / a2)
                cross_asks.append((1 / b1) / b2)
        cross_used = f"1/{usdx} / {yusd}"

    print(f"Collected {len(cross_bids)} valid cross bids and {len(cross_asks)} valid cross asks for cross pair.")
    if cross_bids:
        df.at[idx, 'bid_max'] = max(cross_bids)
        df.at[idx, 'bid_min'] = min(cross_bids)
    if cross_asks:
        df.at[idx, 'ask_max'] = max(cross_asks)
        df.at[idx, 'ask_min'] = min(cross_asks)
    df.at[idx, 'ccypair_used'] = None
    df.at[idx, 'reciprocal'] = None
    df.at[idx, 'cross_used'] = cross_used

    # For cross pairs, set to None (or implement similar logic if needed)
    df.at[idx, 'used_bid'] = None

print("Writing enriched transactions to fx_transactions_with_rates.csv...")
df.to_csv("fx_transactions_with_rates.csv", index=False)
print("fx_transactions_with_rates.csv generated.")
