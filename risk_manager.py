# risk_manager.py

import pandas as pd
import numpy as np

def compute_position_size(df: pd.DataFrame, signal: str, regime: str, config: dict) -> float:
    if signal == "hold":
        return 0.0

    capital = config.get("capital_usdt", 1000)
    risk_fraction = config.get("risk_fraction", 0.01)  # 1% do capital por trade
    min_trade = config.get("min_trade_size", 10)       # mínimo por trade em USDT

    # Cálculo de volatilidade (ATR)
    atr = df["atr_14"].iloc[-1] if "atr_14" in df.columns else 0.005
    price = df["close"].iloc[-1]

    # Ajuste por regime (regimes voláteis → posições menores)
    regime_multiplier = {
        "bull": 1.0,
        "bear": 0.6,
        "sideways": 0.3
    }.get(regime, 0.5)

    # Tamanho em USDT baseado no risco
    risk_usdt = capital * risk_fraction * regime_multiplier
    if atr > 0:
        pos_size = risk_usdt / atr
    else:
        pos_size = risk_usdt / (0.01 * price)  # fallback

    # Converte para quantidade da moeda
    amount = pos_size / price

    # Limita posição mínima
    if amount * price < min_trade:
        return 0.0

    # Arredonda para 6 casas decimais
    return round(amount, 6)
