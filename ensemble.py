import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit

FEATURES = None  # populated dynamically

def _build_dataset(df: pd.DataFrame, horizon: int):
    """Create supervised samples: predict future close at t+h given features at t."""
    X = df.copy()
    y = df["close"].shift(-horizon)  # future close
    data = X.iloc[:-horizon].copy()
    data["target"] = y.iloc[:-horizon]
    # select features (all except date, open/high/low/volume? keep engineered ones)
    feats = [c for c in data.columns if c not in ["date","target","open","high","low","volume"]]
    global FEATURES
    FEATURES = feats
    return data[feats], data["target"]

def _train_model(X, y):
    model = GradientBoostingRegressor(random_state=42)
    model.fit(X, y)
    return model

def train_and_predict_horizons(df_feat: pd.DataFrame, horizon_days: dict):
    preds = {}
    diagnostics = {}
    for label, h in horizon_days.items():
        X, y = _build_dataset(df_feat, h)
        model = _train_model(X, y)
        x_latest = df_feat[FEATURES].iloc[[-1]]
        pred_price = float(model.predict(x_latest)[0])
        preds[label] = pred_price
        diagnostics[label] = {"train_samples": int(len(X))}
    return preds, diagnostics
