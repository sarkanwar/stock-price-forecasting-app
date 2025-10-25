import re
from PyPDF2 import PdfReader

def extract_candidates_from_pdf(file_like):
    reader = PdfReader(file_like)
    text = " ".join([p.extract_text() or "" for p in reader.pages])
    # Extract likely tickers (uppercase words up to 6 chars) and company-like words
    tickers = set(re.findall(r"\b[A-Z]{1,6}\b", text))
    words = set(re.findall(r"\b[A-Za-z][A-Za-z\.\-& ]{2,}\b", text))
    # Merge; keep unique strings
    candidates = list(tickers | {w.strip() for w in words if len(w.strip()) <= 30})
    # Filter obvious non-symbol noise
    blacklist = {"USD","NSE","BSE","NYSE","NASDAQ","LTD","INC","PVT","AND","THE","OF","IN","ON","BY"}
    candidates = [c for c in candidates if c.upper() not in blacklist]
    return candidates
