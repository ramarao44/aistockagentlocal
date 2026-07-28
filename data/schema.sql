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

CREATE TABLE IF NOT EXISTS analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT DEFAULT '1.0',
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    timeframe TEXT,
    ui_json TEXT,
    market_data_json TEXT,
    company_profile_json TEXT,
    technical_json TEXT,
    fundamental_json TEXT,
    sentiment_json TEXT,
    trend_json TEXT,
    ai_json TEXT,
    data_quality TEXT DEFAULT 'unknown'
);

-- Stock catalog for UI dropdown selection (auto-populated by market_fetcher on successful resolution)
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    company_name TEXT,
    exchange TEXT NOT NULL DEFAULT 'NSE',
    sector TEXT,
    isin TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    source TEXT,
    first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_used_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_active ON stocks(active);
CREATE INDEX IF NOT EXISTS idx_stocks_company ON stocks(company_name);

-- =====================================================================
-- Backtest / Evaluation tables (FIS-02 — Evaluation Features)
-- =====================================================================

CREATE TABLE IF NOT EXISTS backtest_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL UNIQUE,
    ts TEXT NOT NULL DEFAULT (datetime('now')),
    timeframe TEXT NOT NULL,
    target TEXT NOT NULL,
    lookback_years INTEGER NOT NULL,
    horizon_periods INTEGER NOT NULL,
    stock_basket_json TEXT NOT NULL,
    signals_json TEXT NOT NULL DEFAULT '[]',
    split_json TEXT,
    aggregate_rmse REAL,
    aggregate_precision REAL,
    aggregate_recall REAL,
    aggregate_f1 REAL,
    aggregate_accuracy REAL,
    confidence_mean REAL,
    probability_mean REAL,
    params_json TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS backtest_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES backtest_runs(run_id),
    symbol TEXT NOT NULL,
    n_periods INTEGER NOT NULL DEFAULT 0,
    rmse REAL,
    precision REAL,
    recall REAL,
    f1 REAL,
    accuracy REAL,
    confidence REAL,
    probability REAL DEFAULT 0.0,
    error TEXT,
    per_stock_json TEXT
);

CREATE TABLE IF NOT EXISTS weight_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES backtest_runs(run_id),
    technical_weight REAL NOT NULL DEFAULT 0.25,
    fundamental_weight REAL NOT NULL DEFAULT 0.25,
    sentiment_weight REAL NOT NULL DEFAULT 0.25,
    trend_weight REAL NOT NULL DEFAULT 0.25,
    global_weight REAL NOT NULL DEFAULT 0.0,
    rsi_weight REAL DEFAULT 0.17,
    volume_breakout_weight REAL DEFAULT 0.17,
    aggregate_accuracy REAL,
    is_best INTEGER NOT NULL DEFAULT 0,
    tuned_from_run_id TEXT,
    ts TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sector_eval_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES backtest_runs(run_id),
    sector TEXT NOT NULL,
    stock_count INTEGER NOT NULL DEFAULT 0,
    avg_rmse REAL,
    avg_precision REAL,
    avg_recall REAL,
    avg_accuracy REAL,
    avg_confidence REAL,
    ts TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_brun_run_id ON backtest_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_bsnap_run_id ON backtest_snapshots(run_id);
CREATE INDEX IF NOT EXISTS idx_bsnap_symbol ON backtest_snapshots(symbol);
CREATE INDEX IF NOT EXISTS idx_wconf_run_id ON weight_configs(run_id);
CREATE INDEX IF NOT EXISTS idx_seval_run_id ON sector_eval_results(run_id);
CREATE INDEX IF NOT EXISTS idx_seval_sector ON sector_eval_results(sector);
