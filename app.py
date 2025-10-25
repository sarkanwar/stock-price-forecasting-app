import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from src.io.pdf_extractor import extract_candidates_from_pdf
from src.io.ticker_lookup import resolve_names_to_tickers
from src.data.price_data import get_history, get_latest_price
from src.features.technical import add_technical_features
from src.models.ensemble import train_and_predict_horizons
from src.trading.backtest import simple_threshold_strategy
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock Predictor", layout="wide")

st.title("📈 Stock Predictor — PDF Upload + Manual Entry")

st.markdown("""
Upload a **PDF** with stock names/tickers *or* type them manually. We'll resolve tickers, fetch data,
and predict prices for several future horizons. **For education only; not financial advice.**
""")

with st.sidebar:
    st.header("Input")
    pdf_file = st.file_uploader("Upload PDF with stock names/tickers", type=["pdf"])
    manual = st.text_area("Or enter names/tickers (comma or newline separated)")
    region = st.text_input("Yahoo Region", value=st.secrets.get("YAHOO_REGION", "US"))
    lang = st.text_input("Yahoo Language", value=st.secrets.get("YAHOO_LANG", "en-US"))
    run_btn = st.button("Run Prediction")

def parse_manual(text: str):
    if not text:
        return []
    raw = [x.strip() for x in text.replace("\n", ",").split(",")]
    return [x for x in raw if x]

candidates = []
if pdf_file is not None:
    try:
        candidates += extract_candidates_from_pdf(pdf_file)
        st.success(f"Found {len(candidates)} candidates in PDF.")
    except Exception as e:
        st.error(f"PDF parse error: {e}")

candidates += parse_manual(manual)
candidates = list(dict.fromkeys(candidates))  # de-duplicate, keep order

if candidates:
    st.write("**Candidates:**", ", ".join(candidates))

if run_btn:
    if not candidates:
        st.warning("Please upload a PDF or enter some names/tickers.")
        st.stop()

    with st.spinner("Resolving names to tickers..."):
        mapping = resolve_names_to_tickers(candidates, region=region, lang=lang)
    st.subheader("Resolved Tickers")
    st.dataframe(pd.DataFrame(mapping.items(), columns=["Input", "Ticker"]))

    tickers = [t for t in mapping.values() if t]
    if not tickers:
        st.error("No valid tickers resolved.")
        st.stop()

    horizon_days = {
        "1D": 1, "1W": 7, "1M": 30, "6M": 180, "1Y": 365, "3Y": 365*3, "5Y": 365*5
    }

    results = []
    for t in tickers:
        with st.spinner(f"Fetching data & predicting for {t}..."):
            try:
                hist = get_history(t, period_years=8)
                if hist is None or len(hist) < 300:
                    st.warning(f"Not enough data for {t}. Skipping.")
                    continue
                df_feat = add_technical_features(hist.copy())
                preds, diagnostics = train_and_predict_horizons(df_feat, horizon_days)
                latest = get_latest_price(hist)
                row = {"Ticker": t, "CurrentPrice": latest}
                # convert preds to price levels
                for k, v in preds.items():
                    row[k] = float(v)
                results.append(row)
            except Exception as e:
                st.error(f"{t}: {e}")

    if results:
        df = pd.DataFrame(results)
        st.subheader("Predicted Prices")
        st.dataframe(df.set_index("Ticker").round(2))

        st.download_button(
            "Download CSV", data=df.to_csv(index=False).encode("utf-8"),
            file_name="predictions.csv", mime="text/csv"
        )

        st.markdown("---")
        st.subheader("Backtest (simple threshold strategy)")
        bt_ticker = st.selectbox("Choose a ticker to backtest", options=[r["Ticker"] for r in results])
        horizon_choice = st.selectbox("Signal horizon", options=list(horizon_days.keys()), index=2)
        threshold = st.slider("Expected return threshold (%)", min_value=-10.0, max_value=20.0, value=3.0, step=0.5)
        years = st.slider("Lookback years", 2, 8, 5)
        if st.button("Run Backtest"):
            hist = get_history(bt_ticker, period_years=years)
            df_feat = add_technical_features(hist.copy())
            bt = simple_threshold_strategy(df_feat, horizon_days[horizon_choice], threshold/100.0)
            st.write("**Backtest Metrics**")
            st.json(bt["metrics"])
            st.line_chart(bt["equity_curve"].set_index("date")["equity"])
    else:
        st.info("No predictions generated.")
