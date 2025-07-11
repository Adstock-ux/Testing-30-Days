# utils.py

import yaml
import logging

def load_config(path: str) -> dict:
    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logging.error(f"[Utils] Erro ao carregar config: {e}")
        return {}

def safe_div(a, b, fallback=0.0):
    try:
        return a / b if b != 0 else fallback
    except:
        return fallback

def format_price(p: float, decimals=2) -> str:
    return f"{p:.{decimals}f}"

def clip(value, min_val, max_val):
    return max(min_val, min(value, max_val))
