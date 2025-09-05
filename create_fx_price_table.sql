CREATE TABLE fx_price
(
    timestamp DateTime64(9),            -- Timestamp in nanoseconds (DateTime64 with 9 decimal places)
    date Date,                          -- Date (for partitioning/filtering)
    bids Array(Float64),                -- Array of bid prices
    asks Array(Float64),                -- Array of ask prices
    qtys Array(Float64),                -- Array of quantities
    ccypair String,                     -- Currency pair (e.g., "EURUSD")
    quoteId String,                     -- Quote identifier
    name String                         -- Name (e.g., source or venue)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(date)
ORDER BY (ccypair, timestamp);

INSERT INTO fx_price (
    timestamp, date, bids, asks, qtys, ccypair, quoteId, name
) VALUES
(
    '2024-06-01 12:00:00.123456789', -- timestamp (nanoseconds)
    '2024-06-01',                    -- date
    [1.0850, 1.0848, 1.0845],        -- bids
    [1.0852, 1.0854, 1.0856],        -- asks
    [100000, 500000, 1000000],       -- qtys
    'EURUSD',                        -- ccypair
    'Q12345',                        -- quoteId
    'TestSource'                     -- name
);
