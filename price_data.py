import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_history(symbol: str, period_years: int = 5):
    end = datetime.utcnow()
    start = end - timedelta(days=365*period_years + 30)
    df = yf.download(symbol, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), auto_adjust=True, progress=False)
    if df is None or df.empty:
        return None
    df = df.reset_index()[["Date","Open","High","Low","Close","Volume"]]
    df.rename(columns={"Date":"date","Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"}, inplace=True)
    df.dropna(inplace=True)
    return df

def get_latest_price(df_hist: pd.DataFrame):
    return float(df_hist["close"].iloc[-1])
