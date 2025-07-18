import asyncio
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import websockets
import nest_asyncio
import numpy as np

nest_asyncio.apply()
live_candles = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# --- Indicator Functions ---
def compute_rsi(data, period=14):
    delta = data['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_macd(data):
    ema12 = data['close'].ewm(span=12).mean()
    ema26 = data['close'].ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd, signal

def compute_ema(data, span=20):
    return data['close'].ewm(span=span).mean()

def compute_sma(data, window=20):
    return data['close'].rolling(window=window).mean()

def compute_bollinger_bands(data, window=20):
    sma = compute_sma(data, window)
    std = data['close'].rolling(window=window).std()
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    return sma, upper, lower

def compute_obv(data):
    obv = [0]
    for i in range(1, len(data)):
        if data['close'][i] > data['close'][i-1]:
            obv.append(obv[-1] + data['volume'][i])
        elif data['close'][i] < data['close'][i-1]:
            obv.append(obv[-1] - data['volume'][i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=data.index)

def compute_cci(data, period=20):
    tp = (data['high'] + data['low'] + data['close']) / 3
    sma = tp.rolling(period).mean()
    mad = tp.rolling(period).apply(lambda x: np.fabs(x - x.mean()).mean())
    return (tp - sma) / (0.015 * mad)

def compute_stochastic(data, k_period=14, d_period=3):
    low_min = data['low'].rolling(window=k_period).min()
    high_max = data['high'].rolling(window=k_period).max()
    k = 100 * ((data['close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_period).mean()
    return k, d

def compute_vwap(data):
    vwap = (data['close'] * data['volume']).cumsum() / data['volume'].cumsum()
    return vwap

def compute_adx(data, period=14):
    plus_dm = data['high'].diff()
    minus_dm = data['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    tr = pd.concat([
        data['high'] - data['low'],
        abs(data['high'] - data['close'].shift()),
        abs(data['low'] - data['close'].shift())
    ], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).sum() / atr)
    minus_di = abs(100 * (minus_dm.rolling(window=period).sum() / atr))
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    return dx.rolling(window=period).mean()

# --- Binance WebSocket ---
async def binance_ws(symbol="btcusdt", interval="1m"):
    url = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"
    global live_candles

    async with websockets.connect(url) as websocket:
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            k = data['k']

            if k['x']:
                candle = {
                    'timestamp': pd.to_datetime(k['t'], unit='ms'),
                    'open': float(k['o']),
                    'high': float(k['h']),
                    'low': float(k['l']),
                    'close': float(k['c']),
                    'volume': float(k['v']),
                }
                new_df = pd.DataFrame([candle])
                live_candles = pd.concat([live_candles, new_df], ignore_index=True)
                live_candles = live_candles.tail(500).reset_index(drop=True)
            await asyncio.sleep(1)

# --- Streamlit UI ---
async def streamlit_app():
    st.set_page_config(page_title="Real-Time Crypto Dashboard", layout="wide")
    st.title("📊 GrooTrading Market Dashboard App")

    symbol = st.sidebar.selectbox("Symbol", ["btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt"])
    interval = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m"])

    st.sidebar.markdown("## Simulate Trade")
    entry_price = st.sidebar.number_input("Your Entry Price ($)", value=0.0, step=0.01)
    amount_usd = st.sidebar.number_input("Amount to Trade ($)", value=100.0, step=10.0)

    price_area = st.empty()
    pnl_area = st.empty()
    chart_area = st.empty()

    while True:
        if not live_candles.empty:
            latest_price = live_candles['close'].iloc[-1]
            price_area.markdown(f"### {symbol.upper()} Live Price: **${latest_price:.2f}**")

            if entry_price > 0:
                quantity = amount_usd / entry_price
                current_value = quantity * latest_price
                profit_loss = current_value - amount_usd
                percent_change = (profit_loss / amount_usd) * 100
                pnl_area.markdown(f"""
                ### Trade Simulation Result
                - Quantity: **{quantity:.6f}** {symbol.upper().replace('USDT', '')}
                - Current Value: **${current_value:.2f}**
                - **PnL:** ${profit_loss:.2f} ({percent_change:.2f}%)
                """)

            # --- Compute Indicators ---
            rsi = compute_rsi(live_candles)
            macd, macd_signal = compute_macd(live_candles)
            ema = compute_ema(live_candles)
            sma = compute_sma(live_candles)
            bb_mid, bb_upper, bb_lower = compute_bollinger_bands(live_candles)
            obv = compute_obv(live_candles)
            cci = compute_cci(live_candles)
            k, d = compute_stochastic(live_candles)
            vwap = compute_vwap(live_candles)
            adx = compute_adx(live_candles)

            # --- Draw Charts ---
            fig, axs = plt.subplots(6, 2, figsize=(16, 20), sharex=True)
            axs = axs.flatten()

            axs[0].plot(live_candles['timestamp'], live_candles['close'], label='Price')
            axs[0].set_title("Price Chart")

            axs[1].plot(live_candles['timestamp'], rsi, label='RSI', color='orange')
            axs[1].axhline(70, linestyle='--', color='red')
            axs[1].axhline(30, linestyle='--', color='green')
            axs[1].set_title("RSI (Relative Strength Index)")

            axs[2].plot(live_candles['timestamp'], macd, label='MACD')
            axs[2].plot(live_candles['timestamp'], macd_signal, label='Signal')
            axs[2].set_title("MACD")

            axs[3].plot(live_candles['timestamp'], ema, label='EMA 20')
            axs[3].set_title("EMA (Exponential MA)")

            axs[4].plot(live_candles['timestamp'], sma, label='SMA 20', color='purple')
            axs[4].set_title("SMA (Simple MA)")

            axs[5].plot(live_candles['timestamp'], bb_mid, label='BB Mid')
            axs[5].plot(live_candles['timestamp'], bb_upper, label='BB Upper')
            axs[5].plot(live_candles['timestamp'], bb_lower, label='BB Lower')
            axs[5].set_title("Bollinger Bands")

            axs[6].plot(live_candles['timestamp'], obv, label='OBV', color='brown')
            axs[6].set_title("OBV (On-Balance Volume)")

            axs[7].plot(live_candles['timestamp'], cci, label='CCI', color='green')
            axs[7].set_title("CCI (Commodity Channel Index)")

            axs[8].plot(live_candles['timestamp'], k, label='%K')
            axs[8].plot(live_candles['timestamp'], d, label='%D')
            axs[8].set_title("Stochastic Oscillator")

            axs[9].plot(live_candles['timestamp'], vwap, label='VWAP', color='blue')
            axs[9].set_title("VWAP (Volume Weighted Avg Price)")

            axs[10].plot(live_candles['timestamp'], adx, label='ADX', color='magenta')
            axs[10].set_title("ADX (Average Directional Index)")

            for ax in axs:
                ax.legend()
                ax.grid(True)

            chart_area.pyplot(fig)
            plt.close(fig)

        await asyncio.sleep(2)

# --- Main ---
def main():
    loop = asyncio.get_event_loop()
    loop.create_task(binance_ws())  # Run WebSocket
    loop.run_until_complete(streamlit_app())

if __name__ == "__main__":
    main()
