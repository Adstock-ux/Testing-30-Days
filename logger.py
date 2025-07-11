# logger.py

import logging
import sqlite3
import os
from datetime import datetime

DB_PATH = "logs/trade_log.db"

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
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_trade(symbol, signal, position_size, regime, order_info, df, config):
    _init_db()

    price = df["close"].iloc[-1]
    timestamp = datetime.utcnow().isoformat()
    status = "executed" if order_info else "skipped"

    logging.info(f"[Logger] {timestamp} | {symbol} | {signal.upper()} | {regime} | Qty: {position_size} | Status: {status}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trades (timestamp, symbol, signal, regime, price, position_size, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, symbol, signal, regime, price, position_size, status))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.warning(f"[Logger] Falha ao gravar no SQLite: {e}")
