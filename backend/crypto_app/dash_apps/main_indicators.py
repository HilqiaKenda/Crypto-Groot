from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from ..tasks.binance_listener import start_ws_thread
import pandas as pd
from .indicators import compute_rsi, compute_ema
from .chart_prices import rsi_price, ema_vs_price_chart
from .candlestick import candlestick_with_volume_and_ema
from .data_store import live_candles
from .app_layout import app



# Start the Binance WebSocket data fetcher in a background thread
start_ws_thread()


@app.callback(
    [
        Output("trade-recommendation", "children"),
        Output("candlestick-container", "children"),
        Output("ema-chart", "figure"),
        Output("rsi-chart", "figure"),
        Output("currency-name", "children"),
        Output("current-price", "children"),
        Output("current-rsi", "children"),
    ],
    [Input("main-update", "n_intervals"), Input("symbol-selector", "value")],
)
def update_main_dashboard(n, symbol):
    df = live_candles.get(symbol, pd.DataFrame()).copy()

    if df.empty or len(df) < 5:
        return (
            html.Div("Waiting for enough data...", style={"color": "#999"}),
            "",         
            go.Figure(),
            go.Figure(),
            "Currency: " + symbol.upper(), 
            "Price: -- USDT",
            "RSI: --"
        )

        # return "Waiting for enough data...", "", go.Figure(), go.Figure(), go.Figure(), "", ""

    
    """Convert timestamps to string for Plotly compatibility"""
    df["timestamp"] = df["timestamp"].astype(str)

    ema = compute_ema(df)
    rsi = compute_rsi(df)

    latest_price = df["close"].iloc[-1]
    latest_ema = ema.iloc[-1]
    latest_rsi = rsi.iloc[-1]


    if latest_rsi < 30:
        if latest_price > latest_ema:
            signal = "🔽 STRONG BUY — RSI is Oversold and Price is Above EMA. Strong upward signal."
            color = "#ff4444"  # Red 
        else:
            signal = "🔽 BUY — RSI is Oversold but Price is Below EMA. Possible rebound ahead."
            color = "#dc3545"  # Red
    elif latest_rsi > 70:
        if latest_price < latest_ema:
            signal = "🔼 STRONG SELL — RSI is Overbought and Price is Below EMA. Strong downward signal."
            color = "#00C851"  # Green
        else:
            signal = "🔼 SELL — RSI is Overbought but Price is Above EMA. May start to drop."
            color = "#28a745"  # Green
    else:
        signal = "⏸ HOLD — No Clear Signal. Market is neutral; best to wait."
        color = "#e5c461"  # Yellow


    """Signal div with dynamic styling"""
    signal_div = html.Div(signal, style={"color": color})

    candle_fig = candlestick_with_volume_and_ema(df=df, symbol=symbol, ema=ema)

    ema_fig = ema_vs_price_chart(df, ema)

    rsi_fig = rsi_price(df, rsi)

    """Display current price and RSI value"""
    currency_name_text = f"Currency: {symbol.upper()}"
    current_price_text = f"Price: {latest_price} USDT"
    current_rsi_text = f"RSI: {latest_rsi:.2f}"

    return signal_div, dcc.Graph(figure=candle_fig), ema_fig, rsi_fig, currency_name_text, current_price_text, current_rsi_text

