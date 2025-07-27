from django_plotly_dash import DjangoDash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from .binance_listener import symbol_candles, start_ws_thread
import pandas as pd
from .indicators import compute_rsi, compute_ema

SYMBOLS = [
    "btcusdt",
    "ethusdt",
    "bnbusdt",
    "solusdt",
    "adausdt",
    "xrpusdt",
    "dogeusdt",
    "dotusdt",
    "maticusdt",
    "ltcusdt",
    "bchusdt",
    "uniusdt",
    "linkusdt",
    "trxusdt",
    "avaxusdt",
    "xlmusdt",
    "nearusdt",
    "filusdt",
    "atomusdt",
    "etcusdt",
    "vetusdt",
    "apeusdt",
    "egldusdt",
    "sandusdt",
    "manausdt",
    "icpusdt",
    "ftmusdt",
    "hbarusdt",
    "algousdt",
    "thetausdt",
    "xtzusdt",
    "aaveusdt",
    "chzusdt",
    "enjusdt",
    "runeusdt",
    "crvusdt",
    "oneusdt",
    "zecusdt",
    "dashusdt",
    "yfiusdt",
    "compusdt",
    "omgusdt",
    "sushiusdt",
    "ankrusdt",
    "lrcusdt",
    "wavesusdt",
    "zilusdt",
    "balusdt",
    "qtumusdt",
    "storjusdt",
]
DEFAULT_SYMBOL = "btcusdt"

app = DjangoDash("MainIndicators")

# Start the Binance WebSocket data fetcher in a background thread
start_ws_thread()

app.layout = html.Div(
    [
        html.H2("📊 Trading Dashboard: EMA, RSI, Candlestick"),
        dcc.Dropdown(
            id="symbol-selector",
            options=[{"label": s.upper(), "value": s} for s in SYMBOLS],
            value=DEFAULT_SYMBOL,
            style={"width": "300px", "marginBottom": "20px"},
        ),
        html.Div(
            id="trade-recommendation", style={"fontSize": "22px", "fontWeight": "bold"}
        ),
        dcc.Interval(id="main-update", interval=5000, n_intervals=0),
        dcc.Graph(id="candlestick-chart"),
        dcc.Graph(id="ema-chart"),
        dcc.Graph(id="rsi-chart"),
    ]
)


@app.callback(
    [
        Output("trade-recommendation", "children"),
        Output("candlestick-chart", "figure"),
        Output("ema-chart", "figure"),
        Output("rsi-chart", "figure"),
    ],
    [Input("main-update", "n_intervals"), Input("symbol-selector", "value")],
)
def update_main_dashboard(n, symbol):
    df = symbol_candles.get(symbol, pd.DataFrame()).copy()

    print(f"[DEBUG] DataFrame shape for {symbol}: {df.shape}")
    print(f"[DEBUG] DataFrame head for {symbol}:\n{df.head()}")

    if df.empty or len(df) < 5:
        return "Waiting for enough data...", go.Figure(), go.Figure(), go.Figure()

    # Convert timestamps to string for Plotly compatibility
    df["timestamp"] = df["timestamp"].astype(str)

    ema = compute_ema(df)
    rsi = compute_rsi(df)

    latest_price = df["close"].iloc[-1]
    latest_ema = ema.iloc[-1]
    latest_rsi = rsi.iloc[-1]

    # === Signal Logic ===
    if latest_rsi < 30 and latest_price > latest_ema:
        signal = "🔼 Buy Signal — RSI Oversold + Price > EMA"
        color = "green"
    elif latest_rsi > 70 and latest_price < latest_ema:
        signal = "🔽 Sell Signal — RSI Overbought + Price < EMA"
        color = "red"
    else:
        signal = "⏸ Hold — No strong signal"
        color = "gray"

    signal_div = html.Div(signal, style={"color": color})

    # === 1. Candlestick with Volume ===
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

    candle_fig.update_layout(
        title=f"{symbol.upper()} Candlestick + Volume",
        yaxis=dict(title="Price"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
        xaxis_rangeslider_visible=False,
        height=500,
    )

    # === 2. EMA Chart ===
    ema_fig = go.Figure()
    ema_fig.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["close"], name="Price", line=dict(color="blue")
        )
    )
    ema_fig.add_trace(
        go.Scatter(x=df["timestamp"], y=ema, name="EMA", line=dict(color="orange"))
    )
    ema_fig.update_layout(title="EMA vs Price", height=400)

    # === 3. RSI Chart ===
    rsi_fig = go.Figure()
    rsi_fig.add_trace(
        go.Scatter(x=df["timestamp"], y=rsi, name="RSI", line=dict(color="purple"))
    )
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
    rsi_fig.update_layout(title="Relative Strength Index", height=300)

    return signal_div, candle_fig, ema_fig, rsi_fig


# from django_plotly_dash import DjangoDash
# from dash import dcc, html, Input, Output
# import plotly.graph_objs as go
# from .binance_listener import symbol_candles
# from .indicators import compute_rsi, compute_ema
# import pandas as pd

# # Define symbols dropdown options
# symbols = list(symbol_candles.keys())
# DEFAULT_SYMBOL = "btcusdt"

# app = DjangoDash("MainIndicators")

# app.layout = html.Div([
#     html.H2("📊 Trading Dashboard: EMA, RSI, Candlestick"),

#     dcc.Dropdown(
#         id='symbol-selector',
#         options=[{"label": s.upper(), "value": s} for s in symbols],
#         value=DEFAULT_SYMBOL,
#         style={"width": "300px", "marginBottom": "20px"}
#     ),

#     html.Div(id='trade-recommendation', style={'fontSize': '22px', 'fontWeight': 'bold'}),

#     dcc.Interval(id='main-update', interval=5000, n_intervals=0),

#     dcc.Graph(id='candlestick-chart'),
#     dcc.Graph(id='ema-chart'),
#     dcc.Graph(id='rsi-chart'),
# ])


# @app.callback(
#     Output('trade-recommendation', 'children'),
#     Output('candlestick-chart', 'figure'),
#     Output('ema-chart', 'figure'),
#     Output('rsi-chart', 'figure'),
#     Input('main-update', 'n_intervals'),
#     Input('symbol-selector', 'value')
# )
# def update_main_dashboard(n, symbol):
#     df = symbol_candles.get(symbol, pd.DataFrame()).copy()

#     if df.empty or len(df) < 30:
#         return "Waiting for enough data...", go.Figure(), go.Figure(), go.Figure()

#     ema = compute_ema(df)
#     rsi = compute_rsi(df)

#     latest_price = df['close'].iloc[-1]
#     latest_ema = ema.iloc[-1]
#     latest_rsi = rsi.iloc[-1]

#     # === Signal Logic ===
#     if latest_rsi < 30 and latest_price > latest_ema:
#         signal = "🔼 Buy Signal — RSI Oversold + Price > EMA"
#         color = "green"
#     elif latest_rsi > 70 and latest_price < latest_ema:
#         signal = "🔽 Sell Signal — RSI Overbought + Price < EMA"
#         color = "red"
#     else:
#         signal = "⏸ Hold — No strong signal"
#         color = "gray"

#     signal_div = html.Div(signal, style={'color': color})

#     # === 1. Candlestick with Volume ===
#     candle_fig = go.Figure()

#     candle_fig.add_trace(go.Candlestick(
#         x=df['timestamp'],
#         open=df['open'],
#         high=df['high'],
#         low=df['low'],
#         close=df['close'],
#         name='Candlestick'
#     ))

#     candle_fig.add_trace(go.Bar(
#         x=df['timestamp'],
#         y=df['volume'],
#         name='Volume',
#         marker_color='rgba(58,71,80,0.3)',
#         yaxis='y2'
#     ))

#     candle_fig.update_layout(
#         title=f"{symbol.upper()} Candlestick + Volume",
#         yaxis=dict(title='Price'),
#         yaxis2=dict(title='Volume', overlaying='y', side='right'),
#         xaxis_rangeslider_visible=False,
#         height=500
#     )

#     # === 2. EMA Chart ===
#     ema_fig = go.Figure()
#     ema_fig.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], name="Price", line=dict(color='blue')))
#     ema_fig.add_trace(go.Scatter(x=df['timestamp'], y=ema, name="EMA", line=dict(color='orange')))
#     ema_fig.update_layout(title="EMA vs Price", height=400)

#     # === 3. RSI Chart ===
#     rsi_fig = go.Figure()
#     rsi_fig.add_trace(go.Scatter(x=df['timestamp'], y=rsi, name="RSI", line=dict(color='purple')))
#     rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
#     rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
#     rsi_fig.update_layout(title="Relative Strength Index", height=300)

#     return signal_div, candle_fig, ema_fig, rsi_fig


# from django_plotly_dash import DjangoDash
# from dash import dcc, html, Input, Output
# import plotly.graph_objs as go
# from .binance_listener import symbol_candles
# from .indicators import compute_rsi, compute_ema
# import pandas as pd

# app = DjangoDash("MainIndicators")

# app.layout = html.Div([
#     html.H2("📊 Principal Trading Indicators: EMA, RSI, Price"),

#     html.Div(id='trade-recommendation', style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#1e293b'}),
#     dcc.Interval(id='main-update', interval=3000, n_intervals=0),

#     dcc.Graph(id='price-graph'),
#     dcc.Graph(id='ema-graph'),
#     dcc.Graph(id='rsi-graph'),
# ])

# @app.callback(
#     Output('trade-recommendation', 'children'),
#     Output('price-graph', 'figure'),
#     Output('ema-graph', 'figure'),
#     Output('rsi-graph', 'figure'),
#     Input('main-update', 'n_intervals')
# )
# def update_main_dashboard(n):
#     df = symbol_candles.get("btcusdt", pd.DataFrame()).copy()
#     if df.empty or len(df) < 5:
#         return "Waiting for enough data...", go.Figure(), go.Figure(), go.Figure()

#     latest_price = df['close'].iloc[-1]
#     ema = compute_ema(df)
#     rsi = compute_rsi(df)

#     latest_ema = ema.iloc[-1]
#     latest_rsi = rsi.iloc[-1]

#     # === Trade Signal Logic ===
#     signal = ""
#     color = "black"

#     if latest_rsi < 30 and latest_price > latest_ema:
#         signal = "🔼 Buy Signal — RSI Oversold + Price above EMA"
#         color = "green"
#     elif latest_rsi > 70 and latest_price < latest_ema:
#         signal = "🔽 Sell Signal — RSI Overbought + Price below EMA"
#         color = "red"
#     else:
#         signal = "⏸ Hold — Market is Neutral"
#         color = "gray"

#     recommendation_msg = html.Div(signal, style={'color': color})

#     # === Graphs ===
#     price_fig = go.Figure()
#     price_fig.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], name="Price", line=dict(color='blue')))
#     price_fig.update_layout(title="Live Price")

#     ema_fig = go.Figure()
#     ema_fig.add_trace(go.Scatter(x=df['timestamp'], y=ema, name="EMA", line=dict(color='orange')))
#     ema_fig.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], name="Price", line=dict(color='blue', dash='dot')))
#     ema_fig.update_layout(title="Exponential Moving Average (EMA)")

#     rsi_fig = go.Figure()
#     rsi_fig.add_trace(go.Scatter(x=df['timestamp'], y=rsi, name="RSI", line=dict(color='purple')))
#     rsi_fig.add_shape(type="line", x0=df['timestamp'].min(), x1=df['timestamp'].max(), y0=70, y1=70,
#                       line=dict(color="red", dash="dash"))
#     rsi_fig.add_shape(type="line", x0=df['timestamp'].min(), x1=df['timestamp'].max(), y0=30, y1=30,
#                       line=dict(color="green", dash="dash"))
#     rsi_fig.update_layout(title="Relative Strength Index (RSI)")

#     return recommendation_msg, price_fig, ema_fig, rsi_fig


# from django_plotly_dash import DjangoDash
# from dash import dcc, html, Input, Output
# import plotly.graph_objs as go
# from .binance_listener import live_candles
# from .indicators import compute_rsi, compute_ema
# app = DjangoDash("MainIndicators")

# print(f"this is app: {app}")


# app.layout = html.Div([
#     html.H2("📊 Principal Trading Indicators: EMA, RSI, Price"),

#     html.Div(id='trade-recommendation', style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#1e293b'}),

#     dcc.Interval(id='main-update', interval=3000, n_intervals=0),

#     dcc.Graph(id='price-graph'),
#     dcc.Graph(id='ema-graph'),
#     dcc.Graph(id='rsi-graph'),
# ])

# @app.callback(
#     Output('trade-recommendation', 'children'),
#     Output('price-graph', 'figure'),
#     Output('ema-graph', 'figure'),
#     Output('rsi-graph', 'figure'),
#     Input('main-update', 'n_intervals')
# )
# def update_main_dashboard(n):
#     df = live_candles.copy()
#     if df.empty or len(df) < 30:
#         return "Waiting for enough data...", go.Figure(), go.Figure(), go.Figure()

#     latest_price = df['close'].iloc[-1]
#     ema = compute_ema(df)
#     rsi = compute_rsi(df)

#     latest_ema = ema.iloc[-1]
#     latest_rsi = rsi.iloc[-1]

#     # === Trade Signal Logic ===
#     signal = ""
#     color = "black"

#     if latest_rsi < 30 and latest_price > latest_ema:
#         signal = "🔼 Buy Signal — RSI Oversold + Price above EMA"
#         color = "green"
#     elif latest_rsi > 70 and latest_price < latest_ema:
#         signal = "🔽 Sell Signal — RSI Overbought + Price below EMA"
#         color = "red"
#     else:
#         signal = "⏸ Hold — Market is Neutral"
#         color = "gray"

#     recommendation_msg = html.Div(signal, style={'color': color})

#     # === Graphs ===

#     price_fig = go.Figure()
#     price_fig.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], name="Price", line=dict(color='blue')))
#     price_fig.update_layout(title="Live Price")

#     ema_fig = go.Figure()
#     ema_fig.add_trace(go.Scatter(x=df['timestamp'], y=ema, name="EMA", line=dict(color='orange')))
#     ema_fig.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], name="Price", line=dict(color='blue', dash='dot')))
#     ema_fig.update_layout(title="Exponential Moving Average (EMA)")

#     rsi_fig = go.Figure()
#     rsi_fig.add_trace(go.Scatter(x=df['timestamp'], y=rsi, name="RSI", line=dict(color='purple')))
#     rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
#     rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
#     rsi_fig.update_layout(title="Relative Strength Index (RSI)")

#     return recommendation_msg, price_fig, ema_fig, rsi_fig
