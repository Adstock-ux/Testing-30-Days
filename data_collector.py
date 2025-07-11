# data_collector.py

import ccxt
import pandas as pd
import time
import logging

def fetch_market_data(symbol, timeframe, config):
    ex_id = config.get("exchange_id", "binance")
    exchange_cls = getattr(ccxt, ex_id)
    exchange = exchange_cls({
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    })

    tf_map = {
        "1m": "1m", "5m": "5m", "15m": "15m",
        "1h": "1h", "4h": "4h", "1d": "1d"
    }
    ccxt_tf = tf_map.get(timeframe)
    if not ccxt_tf:
        raise ValueError(f"Timeframe '{timeframe}' não suportado.")

    limit = config.get("bars_limit", 500)

    for attempt in range(5):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, ccxt_tf, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            logging.warning(f"[DataCollector] Erro ao buscar dados (tentativa {attempt+1}/5): {e}")
            time.sleep(3)

    logging.error("[DataCollector] Falha ao coletar dados após 5 tentativas.")
    return None
