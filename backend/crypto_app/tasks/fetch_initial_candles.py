from crypto_app.dash_apps.data_store import live_candles
import pandas as pd
import requests


def fetch_initial_candles(symbol, interval="1m", limit=100):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        klines = response.json()
        data = [{
            "timestamp": pd.to_datetime(k[0], unit='ms'),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5])
        } for k in klines]

        live_candles[symbol] = pd.DataFrame(data)

    except Exception as e:
        print(f"Failed to fetch initial candles for {symbol.upper()}: {e}")