# risk_manager.py

import numpy as np
import pandas as pd

def compute_position_size(df: pd.DataFrame, signal: str, regime: str, config: dict) -> float:
    """
    Calcula o tamanho de posição baseado em FRAÇÃO DO CAPITAL (config["risk_fraction"]),
    usando o saldo fictício em config["capital_usdt"] e ignorando ATR.
    """
    # Não abre posição se for hold
    if signal.lower() == "hold":
        return 0.0

    # Saldo fictício e fração de investimento
    capital = config.get("capital_usdt", 0.0)
    invest_fraction = config.get("risk_fraction", 1.0)  # ex: 1.0 = 100% do saldo

    # Valor em USDT a ser investido
    pos_size_usd = capital * invest_fraction

    # Preço de mercado atual
    price = df["close"].iloc[-1]

    # Quantidade da moeda a comprar ou vender
    amount = pos_size_usd / price

    # Filtra ordens abaixo do mínimo definido
    min_trade = config.get("min_trade_size", 0.0)
    if amount * price < min_trade:
        return 0.0

    # Arredonda para 6 casas decimais (padrão CCXT)
    return round(amount, 6)

