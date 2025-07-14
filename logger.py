# logger.py

import logging, sqlite3, os, yaml
from datetime import datetime

DB_PATH     = "logs/trade_log.db"
CONFIG_PATH = "config/config.yaml"

def _init_db():
    os.makedirs("logs", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            signal TEXT,
            regime TEXT,
            price REAL,
            position_size REAL,
            status TEXT,
            faux_balance_usdt REAL,
            faux_balance_asset REAL
        )
    """)
    conn.commit()
    conn.close()

def _save_config(config: dict):
    # garante tipos nativos
    config["capital_usdt"]      = float(config["capital_usdt"])
    config["faux_asset_balance"] = float(config["faux_asset_balance"])
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f)

def log_trade(symbol, signal, position_size, regime, order_info, df, config):
    _init_db()
    price     = df["close"].iloc[-1]
    timestamp = datetime.utcnow().isoformat()
    status    = "executed" if order_info else "skipped"

    usdt_balance  = float(config.get("capital_usdt", 0.0))
    asset_balance = float(config.get("faux_asset_balance", 0.0))

    if order_info:
        if signal.lower() == "buy":
            cost = position_size * price
            usdt_balance  -= cost
            asset_balance += position_size
        elif signal.lower() == "sell":
            proceeds = position_size * price
            usdt_balance  += proceeds
            asset_balance -= position_size

        # atualiza e persiste no config
        config["capital_usdt"]       = usdt_balance
        config["faux_asset_balance"] = asset_balance
        _save_config(config)

    logging.info(
        f"[Logger] {timestamp} | {symbol} | {signal.upper()} | {regime} | "
        f"Qty: {position_size} | Status: {status} | "
        f"Saldo USDT: {usdt_balance:.2f} | Saldo Asset: {asset_balance:.6f}"
    )

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trades
              (timestamp, symbol, signal, regime, price, position_size, status, 
               faux_balance_usdt, faux_balance_asset)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, symbol, signal, regime, price, position_size, status,
            usdt_balance, asset_balance
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.warning(f"[Logger] Falha ao gravar no SQLite: {e}")
