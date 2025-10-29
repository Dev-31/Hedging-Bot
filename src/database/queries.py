from database.connection import get_db

def upsert_user(user_id, username):
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, telegram_username) VALUES (?, ?)",
        (user_id, username)
    )
    conn.commit()

def insert_risk_config(user_id, asset, position_size, threshold):
    conn = get_db()
    conn.execute(
        "INSERT INTO risk_config (user_id, asset, position_size, threshold) VALUES (?, ?, ?, ?)",
        (user_id, asset, position_size, threshold)
    )
    conn.commit()

def get_user_risk_config(user_id, asset):
    conn = get_db()
    cur = conn.execute(
        "SELECT * FROM risk_config WHERE user_id = ? AND asset = ? AND is_active = 1",
        (user_id, asset)
    )
    return cur.fetchone()

def insert_hedge_log(user_id, asset, hedge_size, delta, cost):
    conn = get_db()
    conn.execute(
        "INSERT INTO hedge_logs (user_id, asset, hedge_size, delta_exposure, hedge_cost) VALUES (?, ?, ?, ?, ?)",
        (user_id, asset, hedge_size, delta, cost)
    )
    conn.commit()
