# optuna_automl.py

import optuna
import lightgbm as lgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import os

MODEL_PATH = "models/supervised_optuna.pkl"

def _create_target(df: pd.DataFrame) -> pd.Series:
    future_return = df["close"].pct_change(5).shift(-5)
    return (future_return > 0).astype(int)

def _get_features(df: pd.DataFrame) -> pd.DataFrame:
    drop_cols = ["open", "high", "low", "close", "volume", "ret_5", "return_1"]
    return df.drop(columns=[col for col in drop_cols if col in df.columns], errors="ignore")

def objective(trial, X_train, X_val, y_train, y_val):
    params = {
        "objective": "binary",
        "metric": "auc",
        "verbosity": -1,
        "boosting_type": "gbdt",
        "n_estimators": trial.suggest_int("n_estimators", 50, 500),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "num_leaves": trial.suggest_int("num_leaves", 15, 100),
        "min_child_samples": trial.suggest_int("min_child_samples", 10, 100),
    }

    model = lgb.LGBMClassifier(**params)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], early_stopping_rounds=20, verbose=False)
    preds = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, preds)
    return auc

def run_optuna_automl(df: pd.DataFrame, n_trials: int = 30) -> lgb.Booster:
    df = df.copy().dropna()
    y = _create_target(df)
    X = _get_features(df)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_val, y_train, y_val = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: objective(trial, X_train, X_val, y_train, y_val), n_trials=n_trials)

    best_params = study.best_params
    best_params.update({
        "objective": "binary",
        "metric": "auc",
        "verbosity": -1,
        "boosting_type": "gbdt"
    })

    model = lgb.LGBMClassifier(**best_params)
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    return model
