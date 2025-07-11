# execution_engine.py

import ccxt
import logging

# Credenciais da Binance Testnet (hardcoded)
API_KEY = "pC9YpoqOD4nzT7lwiC8hIuR3j2tuDbtsTmeHCrXDoItKRjjoqN8YOhqclfqdGGo0"
API_SECRET = "dv2YpAtCgZLFmIqicDCI7VTvOfAVhUqiCPwjO25YtqtvQYzn4ZQO86VWTSnWMebr"

def _get_exchange():
    """
    Instancia a Binance Testnet usando credenciais hardcoded e
    habilita o modo sandbox nativo do ccxt.
    """
    exchange = ccxt.binance({
        "apiKey": API_KEY,
        "secret": API_SECRET,
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    })
    exchange.set_sandbox_mode(True)
    return exchange

def execute_trade(symbol: str, signal: str, position_size: float, config: dict) -> dict:
    """
    Executa uma ordem de mercado (buy/sell) na Binance Testnet.
    Recebe também 'config' para manter compatibilidade com main.py,
    mas não usa esse parâmetro internamente.
    Retorna o dict de resposta da ordem ou {} caso hold ou erro.
    """
    exchange = _get_exchange()

    try:
        ticker = exchange.fetch_ticker(symbol)
        price = ticker["last"]

        if signal == "buy" and position_size > 0:
            order = exchange.create_order(symbol, "market", "buy", position_size)
            logging.info(f"[Exec] 🟢 BUY {position_size} {symbol} @ {price}")
        elif signal == "sell" and position_size > 0:
            order = exchange.create_order(symbol, "market", "sell", position_size)
            logging.info(f"[Exec] 🔴 SELL {position_size} {symbol} @ {price}")
        else:
            logging.info("[Exec] ⚪ HOLD — nenhuma ordem executada.")
            return {}

        return order

    except Exception as e:
        logging.exception(f"[Exec] Erro ao executar ordem: {e}")
        return {}
