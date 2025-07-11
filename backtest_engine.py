# backtest_engine.py

import pandas as pd
import numpy as np
import logging

def backtest_strategy(df: pd.DataFrame, signal_func, config: dict) -> dict:
    df = df.copy().dropna().reset_index(drop=True)
    capital = config.get("capital_usdt", 1000)
    capital_curve = [capital]
    position = 0.0
    entry_price = 0.0

    for i in range(len(df) - 1):
        current_price = df.loc[i, "close"]
        next_price = df.loc[i + 1, "close"]
        row_slice = df.iloc[:i+1]

        regime = config.get("override_regime", "bull")  # ou detectar se quiser
        signal = signal_func(row_slice, regime)

        if signal == "buy" and position == 0.0:
            entry_price = current_price
            position = capital / entry_price
        elif signal == "sell" and position > 0.0:
            capital = position * current_price
            position = 0.0
        # hold mantém a posição

        equity = capital if position == 0.0 else position * current_price
        capital_curve.append(equity)

    df_result = pd.DataFrame({
        "step": range(len(capital_curve)),
        "equity": capital_curve
    })

    df_result["return"] = df_result["equity"].pct_change()
    df_result["cum_return"] = df_result["equity"] / capital_curve[0] - 1
    df_result["drawdown"] = df_result["equity"] / df_result["equity"].cummax() - 1

    sharpe = df_result["return"].mean() / df_result["return"].std() * np.sqrt(252) if df_result["return"].std() > 0 else 0
    max_drawdown = df_result["drawdown"].min()

    logging.info(f"[Backtest] Sharpe: {sharpe:.2f} | Max DD: {max_drawdown:.2%} | Final Equity: ${df_result['equity'].iloc[-1]:.2f}")

    return {
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "final_equity": df_result["equity"].iloc[-1],
        "curve": df_result
    }
