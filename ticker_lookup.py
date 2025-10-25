import requests

def yahoo_search(name: str, lang="en-US", region="US"):
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": name, "lang": lang, "region": region}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    for q in data.get("quotes", []):
        if q.get("quoteType") in {"EQUITY","ETF"} and q.get("symbol"):
            return q["symbol"]
    return None

def resolve_names_to_tickers(names, lang="en-US", region="US"):
    out = {}
    for n in names:
        try:
            # If user typed a probable ticker already, keep it
            if n.isupper() and len(n) <= 6:
                out[n] = n
                continue
            sym = yahoo_search(n, lang=lang, region=region)
            out[n] = sym
        except Exception:
            out[n] = None
    return out
