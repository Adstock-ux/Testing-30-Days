# logger.py

import logging
import sqlite3
import os
from datetime import datetime
import yaml

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
            faux_balance REAL
        )
    """)
    conn.commit()
    conn.close()

def _save_config(config: dict):
    # converte saldo para float puro antes de gravar
    config["capital_usdt"] = float(config["capital_usdt"])
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f)

def log_trade(symbol, signal, position_size, regime, order_info, df, config):
    _init_db()

    price     = df["close"].iloc[-1]
    timestamp = datetime.utcnow().isoformat()
    status    = "executed" if order_info else "skipped"

    # Saldo atual (pode ser numpy.float64)
    balance = config.get("capital_usdt", 0.0)

    if order_info:
        delta = position_size * price
        if signal.lower() == "buy":
            balance -= delta
        elif signal.lower() == "sell":
            balance += delta

        # atualiza e persiste no config.yaml (agora como Python float)
        config["capital_usdt"] = balance
        _save_config(config)

    logging.info(
        f"[Logger] {timestamp} | {symbol} | {signal.upper()} | {regime} | "
        f"Qty: {position_size} | Status: {status} | Saldo Fictício: {balance:.2f} USDT"
    )

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trades 
              (timestamp, symbol, signal, regime, price, position_size, status, faux_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, symbol, signal, regime, price, position_size, status, float(balance)
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.warning(f"[Logger] Falha ao gravar no SQLite: {e}")
