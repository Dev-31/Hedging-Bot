CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    telegram_username TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    asset TEXT,
    position_size REAL,
    threshold REAL,
    is_active INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hedge_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    asset TEXT,
    hedge_size REAL,
    delta_exposure REAL,
    hedge_cost REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
