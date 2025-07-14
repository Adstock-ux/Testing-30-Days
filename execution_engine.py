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

# execution_engine.py

import logging

def execute_trade(symbol: str, signal: str, position_size: float, config: dict) -> dict:
    """
    Simula a execução de uma ordem de mercado (buy/sell) sem
    chamar nenhuma API real. Retorna um dict “truthy” para
    marcar o trade como executado, ou {} para hold/skip.
    """
    try:
        # Se for hold ou size zero, nada a fazer
        if signal.lower() not in ("buy", "sell") or position_size <= 0:
            logging.info("⚪ HOLD — nenhuma ordem executada (simulada).")
            return {}

        # Simula execução
        logging.info(f"⚪️ Simulated {signal.upper()} {position_size:.6f} {symbol}")
        return {
            "simulated": True,
            "symbol": symbol,
            "side": signal,
            "amount": position_size,
        }

    except Exception as e:
        # Qualquer erro aqui não impede o bot de continuar
        logging.exception(f"[Exec] Simulated execution error (ignored): {e}")
        return {}
