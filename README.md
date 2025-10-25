# Stock Predictor (PDF upload + Manual entry) — Streamlit App

This project lets you:
- Upload a **PDF** with many stock names or tickers, or type them manually
- Resolve names → tickers automatically
- Fetch historical data
- Engineer technical features
- Train an ensemble model per horizon
- Predict prices for: **1 day, 1 week, 1 month, 6 months, 1 year, 3 years, 5 years**
- Run a simple **backtest** strategy
- View results in **Streamlit**

## Quickstart (Local)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to GitHub (make a new repo).
2. In Streamlit Cloud, choose that repo and `app.py` as the entry point.
3. Add the following **secrets** (optional but recommended) in Streamlit:
   - `YAHOO_REGION`: default `US`
   - `YAHOO_LANG`: default `en-US`

## Notes
- This project uses free Yahoo-style endpoints via `yfinance` for historical EOD data (which can be delayed). For **real‑time** quotes, integrate a paid data provider.
- Forecasts are **experimental**. Always validate with backtests and risk management.
