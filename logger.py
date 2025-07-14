# logger.py

import logging
import sqlite3
import os
from datetime import datetime

# importe o helper que instancia a Testnet
from execution_engine import _get_exchange  

DB_PATH = "logs/trade_log.db"

def _init_db():
    os.makedirs("logs", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # adicione uma coluna 'balance' ao schema, se quiser armazenar
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
            balance REAL     -- nova coluna para o saldo
        )
    """)
    conn.commit()
    conn.close()

def log_trade(symbol, signal, position_size, regime, order_info, df, config):
    _init_db()

    price = df["close"].iloc[-1]
    timestamp = datetime.utcnow().isoformat()
    status = "executed" if order_info else "skipped"

    # 1) instancia a Testnet e busca o balanço livre de USDT
    try:
        exchange = _get_exchange()
        bal = exchange.fetch_balance()
        usdt_balance = bal["USDT"]["free"]
    except Exception as e:
        logging.warning(f"[Logger] Não foi possível obter saldo: {e}")
        usdt_balance = None

    # 2) loga tudo junto, incluindo o saldo
    logging.info(
        f"[Logger] {timestamp} | {symbol} | {signal.upper()} | {regime} | "
        f"Qty: {position_size} | Status: {status} | Saldo USDT: {usdt_balance:.2f}"
    )

    # 3) insere no SQLite (caso queira persistir o saldo também)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trades 
              (timestamp, symbol, signal, regime, price, position_size, status, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, symbol, signal, regime, price, position_size, status, usdt_balance
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.warning(f"[Logger] Falha ao gravar no SQLite: {e}")
