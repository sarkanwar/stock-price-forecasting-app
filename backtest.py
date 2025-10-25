import pandas as pd
import numpy as np
from . import metrics as m

def simple_threshold_strategy(df_feat: pd.DataFrame, horizon_days: int, threshold_ret: float = 0.03):
    """
    Signal: go long if expected return over horizon >= threshold.
    We approximate expected return using a simple rule: price above SMA_20 and RSI rising.
    (You can replace with model-predicted returns for walk-forward in future versions.)
    """
    df = df_feat.copy().reset_index(drop=True)
    df["sma_20"] = df["sma_20"] if "sma_20" in df.columns else df["close"].rolling(20).mean()
    df["signal"] = ((df["close"] > df["sma_20"]) & (df["rsi_14"].diff()>0)).astype(int)
    df["fwd_ret"] = df["close"].shift(-horizon_days)/df["close"] - 1.0
    df["strategy_ret"] = df["signal"] * df["fwd_ret"]
    df["equity"] = (1.0 + df["strategy_ret"].fillna(0)).cumprod()
    curve = df[["date","equity"]].dropna().copy()

    metrics = {
        "CAGR": m.cagr(curve),
        "MaxDrawdown": m.max_drawdown(curve),
        "Sharpe": m.sharpe(df["strategy_ret"].dropna())
    }
    return {"equity_curve": curve, "metrics": metrics}
