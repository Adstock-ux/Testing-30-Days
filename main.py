# main.py

import time
import logging
from datetime import datetime

from data_collector import fetch_market_data
from feature_engineering import generate_features
from regime_detection import detect_regime
from model_supervised import predict_signal
from model_rl import decide_action_rl
from execution_engine import execute_trade
from risk_manager import compute_position_size
from logger import log_trade
from utils import load_config

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def run_bot():
    config = load_config("config/config.yaml")
    symbol = config["symbol"]
    timeframe = config["timeframe"]
    rl_enabled = config.get("enable_rl", True)

    logging.info(f"🔁 Starting SuperProbBot for {symbol} on timeframe {timeframe}")

    while True:
        try:
            # 1. Coleta de dados
            df = fetch_market_data(symbol, timeframe, config)
            if df is None or len(df) < config["min_bars"]:
                logging.warning("Dados insuficientes, pulando ciclo.")
                time.sleep(config["sleep_time"])
                continue

            # 2. Feature Engineering
            df = generate_features(df)

            # 3. Detecção de regime
            regime = detect_regime(df)

            # 4. Predição do modelo supervisionado
            signal = predict_signal(df, regime)

            # 5. Modelo RL (se ativado)
            if rl_enabled:
                signal = decide_action_rl(df, regime, prev_signal=signal)

            # 6. Gestão de risco e position sizing
            position_size = compute_position_size(df, signal, regime, config)

            # 7. Execução
            order_info = execute_trade(symbol, signal, position_size, config)

            # 8. Logging
            log_trade(symbol, signal, position_size, regime, order_info, df, config)

        except Exception as e:
            logging.exception(f"Erro inesperado no ciclo principal: {str(e)}")

        # Aguarda para o próximo ciclo
        time.sleep(config["sleep_time"])

if __name__ == "__main__":
    run_bot()
