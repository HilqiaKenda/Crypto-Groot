from django_plotly_dash import DjangoDash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from .binance_listener import symbol_candles, start_ws_thread
import pandas as pd
from .indicators import compute_rsi, compute_ema

SYMBOLS = [
    "btcusdt", "ethusdt", "bnbusdt", "solusdt", "adausdt", "xrpusdt", "dogeusdt", "dotusdt",
    "maticusdt", "ltcusdt", "bchusdt", "uniusdt", "linkusdt", "trxusdt", "avaxusdt", "xlmusdt",
    "nearusdt", "filusdt", "atomusdt", "etcusdt", "vetusdt", "apeusdt", "egldusdt", "sandusdt",
    "manausdt", "icpusdt", "ftmusdt", "hbarusdt", "algousdt", "thetausdt", "xtzusdt", "aaveusdt",
    "chzusdt", "enjusdt", "runeusdt", "crvusdt", "oneusdt", "zecusdt", "dashusdt", "yfiusdt",
    "compusdt", "omgusdt", "sushiusdt", "ankrusdt", "lrcusdt", "wavesusdt", "zilusdt", "balusdt",
    "qtumusdt", "storjusdt",
]
DEFAULT_SYMBOL = "btcusdt"

app = DjangoDash("MainIndicators")

# Start the Binance WebSocket data fetcher in a background thread
start_ws_thread()

app.layout = html.Div(
    style={'textAlign': 'center'},  # Centering the entire layout
    children=[
        # Main header centered
        html.H2("📊 Groot Trading Market Analyze Dashboard", style={'textAlign': 'center'}), 
        
        # Dropdown selector with margin for spacing
        dcc.Dropdown(
            id="symbol-selector",
            options=[{"label": s.upper(), "value": s} for s in SYMBOLS],
            value=DEFAULT_SYMBOL,
            style={"width": "300px", 
                   "marginBottom": "20px", 
                   "marginRight": "10px",
                   "marginLeft": "20px"
                }
        ),

        html.Div(
            id="trade-recommendation",
            style={
                "fontSize": "22px", 
                "fontWeight": "bold", 
                "marginBottom": "20px", 
                "marginLeft": "20px",  # Aligning to the left
                "textAlign": "left"  # Ensuring the text is aligned left within the div
            }
        ),        

        # Interval to update
        dcc.Interval(id="main-update", interval=5000, n_intervals=0),
        
        # Div to display current price and RSI below the dropdown
        html.Div(id="current-price", 
                 style={"fontSize": "18px", 
                        "fontWeight": "bold", 
                        "marginBottom": "10px", 
                        "marginLeft": "20px"}  # Matching left margin
        ),
        html.Div(id="current-rsi", 
                 style={"fontSize": "18px", 
                        "fontWeight": "bold", 
                        "marginBottom": "20px", 
                        "marginLeft": "20px"}  # Matching left margin
        ),
        
        # Candlestick chart and volume
        html.Div(id="candlestick-container", style={"marginTop": "20px"}),  # Margin for spacing
        
        # EMA vs Price chart
        dcc.Graph(id="ema-chart"),
        
        # RSI chart
        dcc.Graph(id="rsi-chart"),
    ]
)

@app.callback(
    [
        Output("trade-recommendation", "children"),
        Output("candlestick-container", "children"),  # Update the container with the candlestick chart
        Output("ema-chart", "figure"),
        Output("rsi-chart", "figure"),
        Output("current-price", "children"),  # Update the current price
        Output("current-rsi", "children"),  # Update the RSI value
    ],
    [Input("main-update", "n_intervals"), Input("symbol-selector", "value")],
)
def update_main_dashboard(n, symbol):
    df = symbol_candles.get(symbol, pd.DataFrame()).copy()

    if df.empty or len(df) < 5:
        return "Waiting for enough data...", "", go.Figure(), go.Figure(), go.Figure(), "", ""

    # Convert timestamps to string for Plotly compatibility
    df["timestamp"] = df["timestamp"].astype(str)

    ema = compute_ema(df)
    rsi = compute_rsi(df)

    latest_price = df["close"].iloc[-1]
    latest_ema = ema.iloc[-1]
    latest_rsi = rsi.iloc[-1]

    # === Hybrid Signal Logic ===
    if latest_rsi < 30:
        if latest_price > latest_ema:
            signal = "🔽 STRONG BUY — RSI is Oversold, Price is Above EMA (Bullish Trend)"
            color = "#ff4444"  # Red
        else:
            signal = "🔽 BUY — RSI is Oversold (Potential Rebound), but Price is Below EMA"
            color = "#dc3545"  # Red
    elif latest_rsi > 70:
        if latest_price < latest_ema:
            signal = "🔼 STRONG SELL — RSI is Overbought, Price is Below EMA (Bearish Trend)"
            color = "#00C851"  # Green
        else:
            signal = "🔼 SELL — RSI is Overbought (Potential Overextension), but Price is Above EMA"
            color = "#28a745"  # Green
    elif latest_price > latest_ema:
        signal = "↗️ WEAK BUY — Price is Above EMA (Bullish Trend), but RSI is Neutral"
        color = "#17a2b8"  # Blue
    elif latest_price < latest_ema:
        signal = "↘️ WEAK SELL — Price is Below EMA (Bearish Trend), but RSI is Neutral"
        color = "#fd7e14"  # Orange
    else:
        signal = "⏸ HOLD — No Clear Signal (Market Conditions are Neutral)"
        color = "#6c757d"  # Gray

    # Signal div with dynamic styling
    signal_div = html.Div(signal, style={"color": color})

    # === 1. Candlestick with Volume and EMA ===
    candle_fig = go.Figure()

    candle_fig.add_trace(
        go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Candlestick",
        )
    )

    candle_fig.add_trace(
        go.Bar(
            x=df["timestamp"],
            y=df["volume"],
            name="Volume",
            marker_color="rgba(58,71,80,0.3)",
            yaxis="y2",
        )
    )

    # Add the Price and EMA to the Candlestick chart
    candle_fig.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["close"], name="Price", line=dict(color="blue")
        )
    )
    candle_fig.add_trace(
        go.Scatter(x=df["timestamp"], y=ema, name="EMA", line=dict(color="orange"))
    )

    candle_fig.update_layout(
        title=f"{symbol.upper()} Candlestick + Volume + EMA",
        title_x=0.5,  # Center the title
        title_xanchor="center",  # Align the title to the center
        yaxis=dict(title="Price"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
        xaxis_rangeslider_visible=False,
        height=500,
    )

    # === 2. EMA vs Price Chart ===
    ema_fig = go.Figure()
    ema_fig.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["close"], name="Price", line=dict(color="blue")
        )
    )
    ema_fig.add_trace(
        go.Scatter(x=df["timestamp"], y=ema, name="EMA", line=dict(color="orange"))
    )
    ema_fig.update_layout(
        title="EMA vs Price",
        title_x=0.5,  # Center the title
        title_xanchor="center",  # Align the title to the center
        height=400,
    )

    # === 3. RSI Chart ===
    rsi_fig = go.Figure()
    rsi_fig.add_trace(
        go.Scatter(x=df["timestamp"], y=rsi, name="RSI", line=dict(color="purple"))
    )
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
    rsi_fig.update_layout(
        title="Relative Strength Index",
        title_x=0.5,  # Center the title
        title_xanchor="center",  # Align the title to the center
        height=300,
    )

    # Display current price and RSI value
    current_price_text = f"Price: {latest_price} USDT"
    current_rsi_text = f"RSI: {latest_rsi:.2f}"

    return signal_div, dcc.Graph(figure=candle_fig), ema_fig, rsi_fig, current_price_text, current_rsi_text
