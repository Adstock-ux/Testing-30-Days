# risk_manager.py

import numpy as np
import pandas as pd

# risk_manager.py

import pandas as pd

def compute_position_size(df: pd.DataFrame, signal: str, regime: str, config: dict) -> float:
    """
    - Em BUY: investe até config["risk_fraction"] de USDT, limitado pelo capital disponível.
    - Em SELL: só vende todo o faux_asset_balance se > 0.
    """
    usdt_balance  = float(config.get("capital_usdt", 0.0))
    asset_balance = float(config.get("faux_asset_balance", 0.0))
    price         = df["close"].iloc[-1]
    min_trade_usd = config.get("min_trade_size", 0.0)

    signal = signal.lower()
    if signal == "hold":
        return 0.0

    if signal == "buy":
        # quanto USD posso usar
        invest_usd = usdt_balance * config.get("risk_fraction", 1.0)
        if invest_usd < min_trade_usd:
            return 0.0

        amount = invest_usd / price
        return round(amount, 6)

    elif signal == "sell":
        # só vende se tiver ativo e o valor for ≥ mínimo
        if asset_balance <= 0:
            return 0.0
        if asset_balance * price < min_trade_usd:
            return 0.0

        # neste exemplo, vende tudo o que tem
        return round(asset_balance, 6)

    # outros casos (não deveria ocorrer)
    return 0.0
