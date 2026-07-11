CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    UNIQUE(ticker, date)
);

CREATE TABLE IF NOT EXISTS technical_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    rsi REAL,
    macd REAL,
    macd_signal REAL,
    macd_hist REAL,
    ma20 REAL,
    ma50 REAL,
    UNIQUE(ticker, date)
);

CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    title TEXT,
    publisher TEXT,
    link TEXT,
    published_at TEXT,
    UNIQUE(ticker, title)
);

CREATE TABLE IF NOT EXISTS sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    title TEXT NOT NULL,
    sentiment REAL,
    UNIQUE(ticker, title)
);

CREATE TABLE IF NOT EXISTS symbol_resolution_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_key TEXT NOT NULL UNIQUE,
    resolved_nse TEXT NOT NULL,
    resolved_bse TEXT NOT NULL,
    source TEXT,
    last_used_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fundamental_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    period TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    pe_ratio REAL,
    pbv_ratio REAL,
    ev_ebitda REAL,
    peg_ratio REAL,
    dividend_yield REAL,
    revenue_qoq REAL,
    revenue_yoy REAL,
    earnings_qoq REAL,
    earnings_yoy REAL,
    roe REAL,
    roa REAL,
    roce REAL,
    net_margin REAL,
    operating_margin REAL,
    debt_to_equity REAL,
    current_ratio REAL,
    quick_ratio REAL,
    beta REAL,
    interest_coverage REAL,
    valuation_json TEXT,
    growth_json TEXT,
    profitability_json TEXT,
    risk_json TEXT,
    financial_ratios_json TEXT,
    statement_snapshot_json TEXT,
    data_quality_json TEXT,
    last_updated TEXT,
    UNIQUE(ticker, period, as_of_date)
);
