# model_rl.py

import numpy as np
import pandas as pd
import os
import warnings

import gymnasium as gym  # ⬅️ usamos gymnasium
from gymnasium import spaces

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

warnings.filterwarnings("ignore")

MODEL_PATH = "models/rl_model.zip"

class TradingEnv(gym.Env):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self.df = df.reset_index(drop=True)
        self.current_step = 0
        self.total_profit = 1.0
        self.position = 0  # -1: vendido, 0: neutro, 1: comprado

        self.action_space = spaces.Discrete(3)  # 0: hold, 1: buy, 2: sell
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(len(self.df.columns),), dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        self.current_step = 0
        self.total_profit = 1.0
        self.position = 0
        return self._next_observation(), {}

    def _next_observation(self):
        obs = self.df.iloc[self.current_step].values.astype(np.float32)
        return obs

    def step(self, action):
        done = False
        reward = 0.0

        prev_price = self.df.iloc[self.current_step]["close"]
        self.current_step += 1

        if self.current_step >= len(self.df) - 1:
            done = True

        curr_price = self.df.iloc[self.current_step]["close"]

        if action == 1:  # buy
            reward = (curr_price - prev_price) / prev_price
        elif action == 2:  # sell
            reward = (prev_price - curr_price) / prev_price
        else:
            reward = 0.0

        self.total_profit *= (1 + reward)

        obs = self._next_observation()
        return obs, reward, done, False, {}

def train_rl_model(df: pd.DataFrame) -> PPO:
    env = TradingEnv(df)
    check_env(env, warn=True)
    model = PPO("MlpPolicy", env, verbose=0)
    model.learn(total_timesteps=10_000)
    model.save(MODEL_PATH)
    return model

def load_or_train_rl(df: pd.DataFrame) -> PPO:
    if os.path.exists(MODEL_PATH):
        return PPO.load(MODEL_PATH)
    else:
        return train_rl_model(df)

def decide_action_rl(df: pd.DataFrame, regime: str, prev_signal: str = "hold") -> str:
    if regime == "sideways":
        return "hold"

    df = df.copy().dropna()
    if len(df) < 100:
        return "hold"

    model = load_or_train_rl(df)
    obs = df.iloc[[-1]].values.astype(np.float32)
    action, _states = model.predict(obs, deterministic=True)

    if action == 1:
        return "buy"
    elif action == 2:
        return "sell"
    else:
        return prev_signal
