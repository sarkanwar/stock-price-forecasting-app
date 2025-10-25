import numpy as np
import pandas as pd

def sma(x, n):
    return x.rolling(n).mean()

def ema(x, n):
    return x.ewm(span=n, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    roll_up = up.ewm(com=period-1, adjust=False).mean()
    roll_down = down.ewm(com=period-1, adjust=False).mean()
    rs = roll_up / (roll_down + 1e-9)
    return 100 - (100 / (1 + rs))

def macd(x, fast=12, slow=26, signal=9):
    ema_fast = ema(x, fast)
    ema_slow = ema(x, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def bollinger_bands(x, n=20, k=2):
    ma = sma(x, n)
    sd = x.rolling(n).std()
    upper = ma + k*sd
    lower = ma - k*sd
    return upper, ma, lower

def add_technical_features(df: pd.DataFrame):
    df = df.copy()
    df["return_1d"] = df["close"].pct_change()
    df["log_return"] = np.log1p(df["return_1d"])
    for n in [5,10,20,50,100,200]:
        df[f"sma_{n}"] = sma(df["close"], n)
        df[f"ema_{n}"] = ema(df["close"], n)
    df["rsi_14"] = rsi(df["close"], 14)
    macd_line, signal, hist = macd(df["close"])
    df["macd"] = macd_line
    df["macd_signal"] = signal
    df["macd_hist"] = hist
    up, mid, low = bollinger_bands(df["close"])
    df["bb_upper"], df["bb_mid"], df["bb_lower"] = up, mid, low
    df["rolling_vol_20"] = df["return_1d"].rolling(20).std()
    # lags
    for l in [1,2,3,5,10]:
        df[f"lag_{l}"] = df["return_1d"].shift(l)
    df.dropna(inplace=True)
    return df
