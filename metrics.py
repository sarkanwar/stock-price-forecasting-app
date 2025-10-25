import numpy as np
import pandas as pd

def cagr(curve: pd.DataFrame, periods_per_year: int = 252):
    e = curve["equity"].iloc[-1]
    n = len(curve)
    yrs = n/periods_per_year
    if yrs <= 0:
        return 0.0
    return float(e**(1/yrs) - 1)

def max_drawdown(curve: pd.DataFrame):
    x = curve["equity"].values
    peak = np.maximum.accumulate(x)
    dd = (x/peak - 1.0).min()
    return float(dd)

def sharpe(returns: pd.Series, risk_free: float = 0.0, periods_per_year: int = 252):
    ex = returns - risk_free/periods_per_year
    mu = ex.mean()
    sigma = ex.std()
    if sigma == 0 or np.isnan(sigma):
        return 0.0
    sr = (mu / sigma) * np.sqrt(periods_per_year)
    return float(sr)
