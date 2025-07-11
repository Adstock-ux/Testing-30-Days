# model_supervised.py

import pandas as pd
import lightgbm as lgb
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

MODEL_PATH = "models/supervised_model.pkl"

def _create_target(df: pd.DataFrame) -> pd.Series:
    future_return = df["close"].pct_change(periods=5).shift(-5)
    return (future_return > 0).astype(int)

def _get_features(df: pd.DataFrame) -> pd.DataFrame:
    drop_cols = ["open", "high", "low", "close", "volume", "ret_5", "return_1"]
    return df.drop(columns=[col for col in drop_cols if col in df.columns], errors="ignore")

def _load_or_train_model(df: pd.DataFrame) -> lgb.LGBMClassifier:
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)

    X = _get_features(df)
    y = _create_target(df)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    model = lgb.LGBMClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.05,
        verbosity=-1
    )

    model.fit(X_train_scaled, y_train)  # <-- sem early stopping

    joblib.dump(model, MODEL_PATH)
    return model

def predict_signal(df: pd.DataFrame, regime: str) -> str:
    if regime == "sideways":
        return "hold"

    df = df.copy().dropna()
    if len(df) < 100:
        return "hold"

    model = _load_or_train_model(df)
    X_live = _get_features(df).iloc[[-1]]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(_get_features(df))  # Refit scaler com todo histórico
    x_input = X_scaled[-1].reshape(1, -1)

    pred = model.predict(x_input)[0]
    return "buy" if pred == 1 else "sell"
