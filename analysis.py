import yfinance as yf
import pandas_ta as ta

def analyze(symbol):
    df = yf.download(symbol, period="6mo", interval="1d", progress=False)
    if df.empty:
        return None

    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.ema(length=20, append=True)
    df.ta.ema(length=50, append=True)

    last = df.iloc[-1]
    score = 0
    reasons = []

    if last["RSI_14"] < 35:
        score += 25
        reasons.append("RSI aşırı satımdan dönüyor")

    if last["MACD_12_26_9"] > last["MACDs_12_26_9"]:
        score += 25
        reasons.append("MACD pozitif kesişim")

    if last["EMA_20"] > last["EMA_50"]:
        score += 20
        reasons.append("EMA20 EMA50'nin üstünde")

    if last["Volume"] > df["Volume"].rolling(20).mean().iloc[-1]:
        score += 20
        reasons.append("Hacim ortalamanın üstünde")

    return {
        "price": round(last["Close"], 2),
        "score": score,
        "reasons": reasons
    }
