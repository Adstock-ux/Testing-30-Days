# regime_detection.py

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

def detect_regime(df: pd.DataFrame, n_clusters: int = 3) -> str:
    df = df.copy()

    # Features para clustering de regime
    df["ret_5"] = df["close"].pct_change(5)
    df["volatility"] = df["close"].rolling(10).std()

    X = df[["ret_5", "volatility"]].dropna().tail(100)

    # Se não houver dados suficientes
    if len(X) < n_clusters:
        return "unknown"

    kmeans = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42)
    labels = kmeans.fit_predict(X)

    latest_label = labels[-1]
    cluster_means = X.groupby(labels).mean()

    # Heurística para mapear os clusters para regimes conhecidos
    trend_scores = cluster_means["ret_5"]
    volatility_scores = cluster_means["volatility"]

    sorted_clusters = trend_scores.sort_values(ascending=False).index.tolist()

    bull_cluster = sorted_clusters[0]
    bear_cluster = sorted_clusters[-1]
    sideways_cluster = list(set(range(n_clusters)) - {bull_cluster, bear_cluster})[0]

    if latest_label == bull_cluster:
        return "bull"
    elif latest_label == bear_cluster:
        return "bear"
    elif latest_label == sideways_cluster:
        return "sideways"
    else:
        return "unknown"
