# feature_engineering.py

import pandas as pd
import numpy as np
import pandas_ta as ta

# Corrige import interno usado por pandas_ta (workaround temporário)
npNaN = np.nan  # substitui o uso obsoleto do pacote pkg_resources/NaN

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Preencher NaNs iniciais com valor neutro
    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

    # Indicadores técnicos
    df["rsi_14"] = ta.rsi(df["close"], length=14)
    df["rsi_7"] = ta.rsi(df["close"], length=7)

    df["ema_20"] = ta.ema(df["close"], length=20)
    df["ema_50"] = ta.ema(df["close"], length=50)
    df["ema_diff"] = df["ema_20"] - df["ema_50"]

    bbands = ta.bbands(df["close"], length=20)
    df["bb_upper"] = bbands["BBU_20_2.0"]
    df["bb_lower"] = bbands["BBL_20_2.0"]
    df["bb_width"] = bbands["BBU_20_2.0"] - bbands["BBL_20_2.0"]

    macd = ta.macd(df["close"])
    df["macd"] = macd["MACD_12_26_9"]
    df["macd_signal"] = macd["MACDs_12_26_9"]
    df["macd_hist"] = macd["MACDh_12_26_9"]

    df["atr_14"] = ta.atr(df["high"], df["low"], df["close"], length=14)
    df["roc"] = ta.roc(df["close"], length=5)

    # Volume
    df["vol_ma_14"] = df["volume"].rolling(window=14).mean()
    df["vol_ratio"] = df["volume"] / df["vol_ma_14"]

    # Retornos
    df["return_1"] = df["close"].pct_change(1)
    df["return_5"] = df["close"].pct_change(5)

    # Direcionalidade simples
    df["price_direction"] = np.where(df["close"] > df["open"], 1, -1)

    # Normalizar colunas numéricas (opcional, depende do modelo)
    df = df.dropna()

    return df
