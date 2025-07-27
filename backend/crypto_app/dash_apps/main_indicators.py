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
        # Centered title
        html.H2(
            "📊 Groot Trading Dashboard: EMA, RSI, Candlestick", 
            style={"textAlign": "center", "marginBottom": "30px", "fontSize": "28px"}
        ),
        
        # Dropdown and recommendation in a row
        html.Div([
            dcc.Dropdown(
                id="symbol-selector",
                options=[{"label": s.upper(), "value": s} for s in SYMBOLS],
                value=DEFAULT_SYMBOL,
                style={"width": "300px", "display": "inline-block"},
            ),
            html.Div(
                id="trade-recommendation", 
                style={
                    "fontSize": "24px", 
                    "fontWeight": "bold", 
                    "display": "inline-block",
                    "marginLeft": "30px",
                    "verticalAlign": "top",
                    "paddingTop": "8px"
                }
            ),
        ], style={"marginBottom": "20px"}),
        
        dcc.Interval(id="main-update", interval=5000, n_intervals=0),
        
        # Main combined chart
        dcc.Graph(id="main-combined-chart", style={"height": "600px"}),
        
        # Row of separate indicator charts
        html.Div([
            html.Div([
                dcc.Graph(id="price-trend-chart")
            ], style={"width": "33%", "display": "inline-block", "padding": "10px"}),
            
            html.Div([
                dcc.Graph(id="volume-chart")
            ], style={"width": "33%", "display": "inline-block", "padding": "10px"}),
            
            html.Div([
                dcc.Graph(id="momentum-chart")
            ], style={"width": "33%", "display": "inline-block", "padding": "10px"}),
        ], style={"marginTop": "20px"}),
    ]
)


@app.callback(
    [
        Output("trade-recommendation", "children"),
        Output("main-combined-chart", "figure"),
        Output("price-trend-chart", "figure"),
        Output("volume-chart", "figure"),
        Output("momentum-chart", "figure"),
    ],
    [Input("main-update", "n_intervals"), Input("symbol-selector", "value")],
)
def update_main_dashboard(n, symbol):
    df = symbol_candles.get(symbol, pd.DataFrame()).copy()

    print(f"[DEBUG] DataFrame shape for {symbol}: {df.shape}")
    print(f"[DEBUG] DataFrame head for {symbol}:\n{df.head()}")

    if df.empty or len(df) < 5:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Waiting for data...", xref="paper", yref="paper", 
                               x=0.5, y=0.5, showarrow=False, font={"size": 16})
        return "Waiting for enough data...", empty_fig, empty_fig, empty_fig, empty_fig

    # Convert timestamps to string for Plotly compatibility
    df["timestamp"] = df["timestamp"].astype(str)

    ema = compute_ema(df)
    rsi = compute_rsi(df)

    latest_price = df["close"].iloc[-1]
    latest_ema = ema.iloc[-1]
    latest_rsi = rsi.iloc[-1]

    print(f"[DEBUG] Latest RSI: {latest_rsi}, Latest Price: {latest_price}, Latest EMA: {latest_ema}")

    # === FIXED Signal Logic ===
    if latest_rsi < 30:
        if latest_price > latest_ema:
            signal = "🔼 STRONG BUY — RSI Oversold + Price > EMA"
            color = "#00C851"  # Bright green
        else:
            signal = "🔼 BUY — RSI Oversold"
            color = "#28a745"  # Green
    elif latest_rsi > 70:
        if latest_price < latest_ema:
            signal = "🔽 STRONG SELL — RSI Overbought + Price < EMA"
            color = "#ff4444"  # Bright red
        else:
            signal = "🔽 SELL — RSI Overbought"
            color = "#dc3545"  # Red
    elif latest_price > latest_ema:
        signal = "↗️ WEAK BUY — Price > EMA"
        color = "#17a2b8"  # Blue
    elif latest_price < latest_ema:
        signal = "↘️ WEAK SELL — Price < EMA"
        color = "#fd7e14"  # Orange
    else:
        signal = "⏸ HOLD — No clear signal"
        color = "#6c757d"  # Gray

    signal_div = html.Div([
        html.Span(f"Current Price: ${latest_price:.4f} | ", style={"color": "black"}),
        html.Span(f"RSI: {latest_rsi:.1f} | ", style={"color": "purple"}),
        html.Span(signal, style={"color": color, "fontWeight": "bold"})
    ])

    # === 1. MAIN COMBINED CHART ===
    main_fig = go.Figure()

    # Candlesticks
    main_fig.add_trace(
        go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
            yaxis="y1"
        )
    )

    # EMA line
    main_fig.add_trace(
        go.Scatter(
            x=df["timestamp"], 
            y=ema, 
            name="EMA", 
            line=dict(color="#FF6B35", width=2),
            yaxis="y1"
        )
    )

    # RSI on secondary y-axis
    main_fig.add_trace(
        go.Scatter(
            x=df["timestamp"], 
            y=rsi, 
            name="RSI", 
            line=dict(color="#7B68EE", width=2),
            yaxis="y2"
        )
    )

    # RSI reference lines
    main_fig.add_hline(y=70, line_dash="dash", line_color="#FF6B6B", line_width=1, yref="y2")
    main_fig.add_hline(y=30, line_dash="dash", line_color="#4ECDC4", line_width=1, yref="y2")

    main_fig.update_layout(
        title=f"{symbol.upper()} - Price, EMA & RSI Combined",
        yaxis=dict(title="Price ($)", side="left", color="#2C3E50"),
        yaxis2=dict(title="RSI", overlaying="y", side="right", color="#7B68EE", range=[0, 100]),
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_white",
        hovermode="x unified"
    )

    # === 2. PRICE TREND CHART ===
    trend_fig = go.Figure()
    trend_fig.add_trace(
        go.Scatter(
            x=df["timestamp"], 
            y=df["close"], 
            name="Close Price", 
            line=dict(color="#3498DB", width=3),
            fill="tonexty"
        )
    )
    trend_fig.add_trace(
        go.Scatter(
            x=df["timestamp"], 
            y=ema, 
            name="EMA Trend", 
            line=dict(color="#E74C3C", width=2, dash="dot")
        )
    )
    trend_fig.update_layout(
        title="Price Trend Analysis", 
        height=300,
        template="plotly_white",
        showlegend=True
    )

    # === 3. VOLUME CHART ===
    volume_fig = go.Figure()
    volume_fig.add_trace(
        go.Bar(
            x=df["timestamp"],
            y=df["volume"],
            name="Volume",
            marker_color="#9B59B6",
            opacity=0.7
        )
    )
    volume_fig.update_layout(
        title="Trading Volume", 
        height=300,
        template="plotly_white",
        yaxis_title="Volume"
    )

    # === 4. MOMENTUM CHART ===
    momentum_fig = go.Figure()
    
    # RSI with colored background zones
    momentum_fig.add_trace(
        go.Scatter(
            x=df["timestamp"], 
            y=rsi, 
            name="RSI", 
            line=dict(color="#8E44AD", width=3)
        )
    )
    
    # Color zones
    momentum_fig.add_hrect(y0=70, y1=100, fillcolor="#FFE5E5", opacity=0.3, line_width=0)
    momentum_fig.add_hrect(y0=0, y1=30, fillcolor="#E5F5F5", opacity=0.3, line_width=0)
    momentum_fig.add_hrect(y0=30, y1=70, fillcolor="#F0F0F0", opacity=0.2, line_width=0)
    
    momentum_fig.add_hline(y=70, line_dash="dash", line_color="#E74C3C", line_width=2)
    momentum_fig.add_hline(y=50, line_dash="dot", line_color="#95A5A6", line_width=1)
    momentum_fig.add_hline(y=30, line_dash="dash", line_color="#27AE60", line_width=2)
    
    momentum_fig.update_layout(
        title="RSI Momentum", 
        height=300,
        template="plotly_white",
        yaxis=dict(range=[0, 100], title="RSI Value")
    )

    return signal_div, main_fig, trend_fig, volume_fig, momentum_fig



# from django_plotly_dash import DjangoDash
# from dash import dcc, html, Input, Output
# import plotly.graph_objs as go
# from .binance_listener import symbol_candles, start_ws_thread
# import pandas as pd
# from .indicators import compute_rsi, compute_ema

# SYMBOLS = [
#     "btcusdt",
#     "ethusdt",
#     "bnbusdt",
#     "solusdt",
#     "adausdt",
#     "xrpusdt",
#     "dogeusdt",
#     "dotusdt",
#     "maticusdt",
#     "ltcusdt",
#     "bchusdt",
#     "uniusdt",
#     "linkusdt",
#     "trxusdt",
#     "avaxusdt",
#     "xlmusdt",
#     "nearusdt",
#     "filusdt",
#     "atomusdt",
#     "etcusdt",
#     "vetusdt",
#     "apeusdt",
#     "egldusdt",
#     "sandusdt",
#     "manausdt",
#     "icpusdt",
#     "ftmusdt",
#     "hbarusdt",
#     "algousdt",
#     "thetausdt",
#     "xtzusdt",
#     "aaveusdt",
#     "chzusdt",
#     "enjusdt",
#     "runeusdt",
#     "crvusdt",
#     "oneusdt",
#     "zecusdt",
#     "dashusdt",
#     "yfiusdt",
#     "compusdt",
#     "omgusdt",
#     "sushiusdt",
#     "ankrusdt",
#     "lrcusdt",
#     "wavesusdt",
#     "zilusdt",
#     "balusdt",
#     "qtumusdt",
#     "storjusdt",
# ]
# DEFAULT_SYMBOL = "btcusdt"

# app = DjangoDash("MainIndicators")

# # Start the Binance WebSocket data fetcher in a background thread
# start_ws_thread()

# app.layout = html.Div(
#     [
#         # Centered title
#         html.H1(
#             "📊 Trading Dashboard: EMA, RSI, Candlestick",
#             style={
#                 "textAlign": "center",
#                 "marginBottom": "30px",
#                 "color": "#2c3e50",
#                 "fontFamily": "Arial, sans-serif"
#             }
#         ),
        
#         # Controls section
#         html.Div([
#             dcc.Dropdown(
#                 id="symbol-selector",
#                 options=[{"label": s.upper(), "value": s} for s in SYMBOLS],
#                 value=DEFAULT_SYMBOL,
#                 style={"width": "300px", "marginBottom": "20px"},
#             ),
#         ], style={"textAlign": "center"}),
        
#         # Price and recommendation display
#         html.Div([
#             html.Div(id="current-price", style={
#                 "fontSize": "24px", 
#                 "fontWeight": "bold",
#                 "marginBottom": "10px",
#                 "color": "#2c3e50"
#             }),
#             html.Div(id="trade-recommendation", style={
#                 "fontSize": "22px", 
#                 "fontWeight": "bold",
#                 "marginBottom": "20px"
#             }),
#         ], style={"textAlign": "center"}),
        
#         dcc.Interval(id="main-update", interval=5000, n_intervals=0),
        
#         # Main combined chart
#         dcc.Graph(id="main-chart"),
        
#         # Separate EMA and RSI charts for detailed view
#         html.Div([
#             html.Div([
#                 dcc.Graph(id="ema-chart")
#             ], style={"width": "50%", "display": "inline-block"}),
#             html.Div([
#                 dcc.Graph(id="rsi-chart")
#             ], style={"width": "50%", "display": "inline-block"}),
#         ]),
#     ]
# )


# @app.callback(
#     [
#         Output("current-price", "children"),
#         Output("trade-recommendation", "children"),
#         Output("main-chart", "figure"),
#         Output("ema-chart", "figure"),
#         Output("rsi-chart", "figure"),
#     ],
#     [Input("main-update", "n_intervals"), Input("symbol-selector", "value")],
# )
# def update_main_dashboard(n, symbol):
#     df = symbol_candles.get(symbol, pd.DataFrame()).copy()

#     print(f"[DEBUG] DataFrame shape for {symbol}: {df.shape}")
#     print(f"[DEBUG] DataFrame head for {symbol}:\n{df.head()}")

#     if df.empty or len(df) < 5:
#         return (
#             "Waiting for data...", 
#             "Waiting for enough data...", 
#             go.Figure(), 
#             go.Figure(), 
#             go.Figure()
#         )

#     # Convert timestamps to string for Plotly compatibility
#     df["timestamp"] = df["timestamp"].astype(str)

#     ema = compute_ema(df)
#     rsi = compute_rsi(df)

#     latest_price = df["close"].iloc[-1]
#     latest_ema = ema.iloc[-1]
#     latest_rsi = rsi.iloc[-1]

#     # Price display
#     price_display = f"{symbol.upper()}: ${latest_price:.4f}"

#     # === FIXED Signal Logic ===
#     print(f"[DEBUG] Latest RSI: {latest_rsi}, Latest Price: {latest_price}, Latest EMA: {latest_ema}")
    
#     if latest_rsi < 30 and latest_price > latest_ema:
#         signal = "🔼 BUY SIGNAL — RSI Oversold + Price > EMA"
#         signal_color = "#27ae60"  # Green
#     elif latest_rsi > 70 and latest_price < latest_ema:
#         signal = "🔽 SELL SIGNAL — RSI Overbought + Price < EMA"
#         signal_color = "#e74c3c"  # Red
#     elif latest_rsi > 70:
#         signal = "⚠️ CAUTION — RSI Overbought (Consider Selling)"
#         signal_color = "#f39c12"  # Orange
#     elif latest_rsi < 30:
#         signal = "⚠️ CAUTION — RSI Oversold (Consider Buying)"
#         signal_color = "#f39c12"  # Orange
#     else:
#         signal = "⏸ HOLD — No strong signal"
#         signal_color = "#7f8c8d"  # Gray

#     signal_div = html.Div(signal, style={"color": signal_color})

#     # === 1. MAIN COMBINED CHART ===
#     from plotly.subplots import make_subplots
    
#     # Create subplots with secondary y-axis
#     main_fig = make_subplots(
#         rows=3, cols=1,
#         shared_xaxes=True,
#         vertical_spacing=0.03,
#         subplot_titles=('Price & EMA', 'Volume', 'RSI'),
#         row_heights=[0.6, 0.2, 0.2]
#     )

#     # Candlestick chart
#     main_fig.add_trace(
#         go.Candlestick(
#             x=df["timestamp"],
#             open=df["open"],
#             high=df["high"],
#             low=df["low"],
#             close=df["close"],
#             name="Price",
#             increasing_line_color="#27ae60",  # Green for up candles
#             decreasing_line_color="#e74c3c",  # Red for down candles
#         ),
#         row=1, col=1
#     )

#     # EMA line on price chart
#     main_fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"], 
#             y=ema, 
#             name="EMA", 
#             line=dict(color="#3498db", width=2),  # Blue
#             mode='lines'
#         ),
#         row=1, col=1
#     )

#     # Volume chart
#     main_fig.add_trace(
#         go.Bar(
#             x=df["timestamp"],
#             y=df["volume"],
#             name="Volume",
#             marker_color="#95a5a6",  # Gray
#             showlegend=False
#         ),
#         row=2, col=1
#     )

#     # RSI chart
#     main_fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"], 
#             y=rsi, 
#             name="RSI", 
#             line=dict(color="#9b59b6", width=2),  # Purple
#             mode='lines'
#         ),
#         row=3, col=1
#     )

#     # Add RSI reference lines
#     main_fig.add_hline(y=70, line_dash="dash", line_color="#e74c3c", row=3, col=1)
#     main_fig.add_hline(y=30, line_dash="dash", line_color="#27ae60", row=3, col=1)
#     main_fig.add_hline(y=50, line_dash="dot", line_color="#7f8c8d", row=3, col=1)

#     main_fig.update_layout(
#         title=f"{symbol.upper()} - Complete Technical Analysis",
#         height=800,
#         showlegend=True,
#         xaxis_rangeslider_visible=False,
#     )

#     # Update y-axes
#     main_fig.update_yaxes(title_text="Price ($)", row=1, col=1)
#     main_fig.update_yaxes(title_text="Volume", row=2, col=1)
#     main_fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])

#     # === 2. Detailed EMA Chart ===
#     ema_fig = go.Figure()
#     ema_fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"], 
#             y=df["close"], 
#             name="Price", 
#             line=dict(color="#2c3e50", width=2)  # Dark blue
#         )
#     )
#     ema_fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"], 
#             y=ema, 
#             name="EMA", 
#             line=dict(color="#e67e22", width=2)  # Orange
#         )
#     )
#     ema_fig.update_layout(
#         title="Price vs EMA Detailed View", 
#         height=400,
#         yaxis_title="Price ($)"
#     )

#     # === 3. Detailed RSI Chart ===
#     rsi_fig = go.Figure()
#     rsi_fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"], 
#             y=rsi, 
#             name="RSI", 
#             line=dict(color="#8e44ad", width=3),  # Purple
#             fill='tonexty'
#         )
#     )
    
#     # Add colored zones
#     rsi_fig.add_hrect(y0=70, y1=100, fillcolor="#e74c3c", opacity=0.1, line_width=0)
#     rsi_fig.add_hrect(y0=0, y1=30, fillcolor="#27ae60", opacity=0.1, line_width=0)
#     rsi_fig.add_hrect(y0=30, y1=70, fillcolor="#f8f9fa", opacity=0.1, line_width=0)
    
#     rsi_fig.add_hline(y=70, line_dash="dash", line_color="#e74c3c", annotation_text="Overbought")
#     rsi_fig.add_hline(y=30, line_dash="dash", line_color="#27ae60", annotation_text="Oversold")
#     rsi_fig.add_hline(y=50, line_dash="dot", line_color="#7f8c8d", annotation_text="Neutral")
    
#     rsi_fig.update_layout(
#         title="RSI Detailed View", 
#         height=400,
#         yaxis=dict(title="RSI Value", range=[0, 100])
#     )

#     return price_display, signal_div, main_fig, ema_fig, rsi_fig


# from django_plotly_dash import DjangoDash
# from dash import dcc, html, Input, Output
# import plotly.graph_objs as go
# from plotly.subplots import make_subplots
# from .binance_listener import symbol_candles, start_ws_thread
# import pandas as pd
# from .indicators import compute_rsi, compute_ema

# SYMBOLS = [
#     "btcusdt",
#     "ethusdt",
#     "bnbusdt",
#     "solusdt",
#     "adausdt",
#     "xrpusdt",
#     "dogeusdt",
#     "dotusdt",
#     "maticusdt",
#     "ltcusdt",
#     "bchusdt",
#     "uniusdt",
#     "linkusdt",
#     "trxusdt",
#     "avaxusdt",
#     "xlmusdt",
#     "nearusdt",
#     "filusdt",
#     "atomusdt",
#     "etcusdt",
#     "vetusdt",
#     "apeusdt",
#     "egldusdt",
#     "sandusdt",
#     "manausdt",
#     "icpusdt",
#     "ftmusdt",
#     "hbarusdt",
#     "algousdt",
#     "thetausdt",
#     "xtzusdt",
#     "aaveusdt",
#     "chzusdt",
#     "enjusdt",
#     "runeusdt",
#     "crvusdt",
#     "oneusdt",
#     "zecusdt",
#     "dashusdt",
#     "yfiusdt",
#     "compusdt",
#     "omgusdt",
#     "sushiusdt",
#     "ankrusdt",
#     "lrcusdt",
#     "wavesusdt",
#     "zilusdt",
#     "balusdt",
#     "qtumusdt",
#     "storjusdt",
# ]
# DEFAULT_SYMBOL = "btcusdt"

# app = DjangoDash("MainIndicators")

# # Start the Binance WebSocket data fetcher in a background thread
# start_ws_thread()

# app.layout = html.Div(
#     [
#         # Centered title
#         html.H2(
#             "📊 Trading Dashboard: EMA, RSI, Candlestick",
#             style={
#                 "textAlign": "center",
#                 "marginBottom": "30px",
#                 "color": "#2c3e50",
#                 "fontFamily": "Arial, sans-serif"
#             }
#         ),
        
#         # Controls container
#         html.Div([
#             dcc.Dropdown(
#                 id="symbol-selector",
#                 options=[{"label": s.upper(), "value": s} for s in SYMBOLS],
#                 value=DEFAULT_SYMBOL,
#                 style={"width": "300px", "marginBottom": "20px"},
#             ),
#         ], style={"textAlign": "center"}),
        
#         # Trade recommendation
#         html.Div(
#             id="trade-recommendation", 
#             style={
#                 "fontSize": "22px", 
#                 "fontWeight": "bold",
#                 "textAlign": "center",
#                 "marginBottom": "20px"
#             }
#         ),
        
#         dcc.Interval(id="main-update", interval=5000, n_intervals=0),
        
#         # Main combined chart
#         dcc.Graph(id="main-chart"),
        
#         # Separate RSI chart below
#         dcc.Graph(id="rsi-chart"),
#     ]
# )


# @app.callback(
#     [
#         Output("trade-recommendation", "children"),
#         Output("main-chart", "figure"),
#         Output("rsi-chart", "figure"),
#     ],
#     [Input("main-update", "n_intervals"), Input("symbol-selector", "value")],
# )
# def update_main_dashboard(n, symbol):
#     df = symbol_candles.get(symbol, pd.DataFrame()).copy()

#     print(f"[DEBUG] DataFrame shape for {symbol}: {df.shape}")
#     print(f"[DEBUG] DataFrame head for {symbol}:\n{df.head()}")

#     if df.empty or len(df) < 5:
#         return "Waiting for enough data...", go.Figure(), go.Figure()

#     # Convert timestamps to string for Plotly compatibility
#     df["timestamp"] = df["timestamp"].astype(str)

#     ema = compute_ema(df)
#     rsi = compute_rsi(df)

#     latest_price = df["close"].iloc[-1]
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

#     signal_div = html.Div(signal, style={"color": color})

#     # === 1. Main Chart: Candlestick + EMA + Price Line + Volume ===
#     # Create subplot with secondary y-axis for volume
#     main_fig = make_subplots(
#         rows=1, cols=1,
#         specs=[[{"secondary_y": True}]],
#         subplot_titles=[f"{symbol.upper()} - Price Analysis"]
#     )

#     # Add Candlestick chart
#     main_fig.add_trace(
#         go.Candlestick(
#             x=df["timestamp"],
#             open=df["open"],
#             high=df["high"],
#             low=df["low"],
#             close=df["close"],
#             name="Candlestick",
#             increasing_line_color='#00ff88',  # Green for up candles
#             decreasing_line_color='#ff4444',  # Red for down candles
#         ),
#         secondary_y=False,
#     )

#     # Add EMA line
#     main_fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"], 
#             y=ema, 
#             name="EMA",
#             line=dict(color="#ff9500", width=2),  # Orange EMA line
#             mode='lines'
#         ),
#         secondary_y=False,
#     )

#     # Add Price line (close price)
#     main_fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"], 
#             y=df["close"], 
#             name="Close Price",
#             line=dict(color="#0099ff", width=2, dash='dot'),  # Blue dotted price line
#             mode='lines'
#         ),
#         secondary_y=False,
#     )

#     # Add Volume bars on secondary y-axis
#     main_fig.add_trace(
#         go.Bar(
#             x=df["timestamp"],
#             y=df["volume"],
#             name="Volume",
#             marker_color="rgba(128,128,128,0.3)",  # Light gray volume bars
#             opacity=0.6,
#         ),
#         secondary_y=True,
#     )

#     # Update layout for main chart
#     main_fig.update_layout(
#         title={
#             'text': f"{symbol.upper()} - Candlestick, EMA & Price Analysis",
#             'x': 0.5,
#             'xanchor': 'center'
#         },
#         xaxis_rangeslider_visible=False,
#         height=600,
#         showlegend=True,
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         ),
#         plot_bgcolor='rgba(240,240,240,0.1)',
#         paper_bgcolor='white'
#     )

#     # Set y-axes titles
#     main_fig.update_yaxes(title_text="Price ($)", secondary_y=False)
#     main_fig.update_yaxes(title_text="Volume", secondary_y=True)

#     # === 2. RSI Chart (Separate) ===
#     rsi_fig = go.Figure()
    
#     # Add RSI line
#     rsi_fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"], 
#             y=rsi, 
#             name="RSI",
#             line=dict(color="#9c27b0", width=3),  # Purple RSI line
#             fill='tonexty',
#             fillcolor="rgba(156,39,176,0.1)"
#         )
#     )
    
#     # Add overbought and oversold lines
#     rsi_fig.add_hline(y=70, line_dash="dash", line_color="#ff4444", line_width=2, annotation_text="Overbought (70)")
#     rsi_fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", line_width=2, annotation_text="Oversold (30)")
#     rsi_fig.add_hline(y=50, line_dash="dot", line_color="#888888", line_width=1, annotation_text="Neutral (50)")
    
#     # Add colored background zones
#     rsi_fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,68,68,0.1)", layer="below", line_width=0)  # Overbought zone
#     rsi_fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,255,136,0.1)", layer="below", line_width=0)   # Oversold zone
    
#     rsi_fig.update_layout(
#         title={
#             'text': "Relative Strength Index (RSI)",
#             'x': 0.5,
#             'xanchor': 'center'
#         },
#         height=300,
#         yaxis=dict(range=[0, 100], title="RSI"),
#         xaxis=dict(title="Time"),
#         plot_bgcolor='rgba(240,240,240,0.1)',
#         paper_bgcolor='white',
#         showlegend=False
#     )

#     return signal_div, main_fig, rsi_fig





# from django_plotly_dash import DjangoDash
# from dash import dcc, html, Input, Output
# import plotly.graph_objs as go
# from .binance_listener import symbol_candles, start_ws_thread
# import pandas as pd
# from .indicators import compute_rsi, compute_ema

# SYMBOLS = [
#     "btcusdt",
#     "ethusdt",
#     "bnbusdt",
#     "solusdt",
#     "adausdt",
#     "xrpusdt",
#     "dogeusdt",
#     "dotusdt",
#     "maticusdt",
#     "ltcusdt",
#     "bchusdt",
#     "uniusdt",
#     "linkusdt",
#     "trxusdt",
#     "avaxusdt",
#     "xlmusdt",
#     "nearusdt",
#     "filusdt",
#     "atomusdt",
#     "etcusdt",
#     "vetusdt",
#     "apeusdt",
#     "egldusdt",
#     "sandusdt",
#     "manausdt",
#     "icpusdt",
#     "ftmusdt",
#     "hbarusdt",
#     "algousdt",
#     "thetausdt",
#     "xtzusdt",
#     "aaveusdt",
#     "chzusdt",
#     "enjusdt",
#     "runeusdt",
#     "crvusdt",
#     "oneusdt",
#     "zecusdt",
#     "dashusdt",
#     "yfiusdt",
#     "compusdt",
#     "omgusdt",
#     "sushiusdt",
#     "ankrusdt",
#     "lrcusdt",
#     "wavesusdt",
#     "zilusdt",
#     "balusdt",
#     "qtumusdt",
#     "storjusdt",
# ]
# DEFAULT_SYMBOL = "btcusdt"

# app = DjangoDash("MainIndicators")

# # Start the Binance WebSocket data fetcher in a background thread
# start_ws_thread()

# app.layout = html.Div(
#     [
#         html.H2("📊 Trading Dashboard: EMA, RSI, Candlestick"),
#         dcc.Dropdown(
#             id="symbol-selector",
#             options=[{"label": s.upper(), "value": s} for s in SYMBOLS],
#             value=DEFAULT_SYMBOL,
#             style={"width": "300px", "marginBottom": "20px"},
#         ),
#         html.Div(
#             id="trade-recommendation", style={"fontSize": "22px", "fontWeight": "bold"}
#         ),
#         dcc.Interval(id="main-update", interval=5000, n_intervals=0),
#         dcc.Graph(id="candlestick-chart"),
#         dcc.Graph(id="ema-chart"),
#         dcc.Graph(id="rsi-chart"),
#     ]
# )


# @app.callback(
#     [
#         Output("trade-recommendation", "children"),
#         Output("candlestick-chart", "figure"),
#         Output("ema-chart", "figure"),
#         Output("rsi-chart", "figure"),
#     ],
#     [Input("main-update", "n_intervals"), Input("symbol-selector", "value")],
# )
# def update_main_dashboard(n, symbol):
#     df = symbol_candles.get(symbol, pd.DataFrame()).copy()

#     print(f"[DEBUG] DataFrame shape for {symbol}: {df.shape}")
#     print(f"[DEBUG] DataFrame head for {symbol}:\n{df.head()}")

#     if df.empty or len(df) < 5:
#         return "Waiting for enough data...", go.Figure(), go.Figure(), go.Figure()

#     # Convert timestamps to string for Plotly compatibility
#     df["timestamp"] = df["timestamp"].astype(str)

#     ema = compute_ema(df)
#     rsi = compute_rsi(df)

#     latest_price = df["close"].iloc[-1]
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

#     signal_div = html.Div(signal, style={"color": color})

#     # === 1. Candlestick with Volume ===
#     candle_fig = go.Figure()

#     candle_fig.add_trace(
#         go.Candlestick(
#             x=df["timestamp"],
#             open=df["open"],
#             high=df["high"],
#             low=df["low"],
#             close=df["close"],
#             name="Candlestick",
#         )
#     )

#     candle_fig.add_trace(
#         go.Bar(
#             x=df["timestamp"],
#             y=df["volume"],
#             name="Volume",
#             marker_color="rgba(58,71,80,0.3)",
#             yaxis="y2",
#         )
#     )

#     candle_fig.update_layout(
#         title=f"{symbol.upper()} Candlestick + Volume",
#         yaxis=dict(title="Price"),
#         yaxis2=dict(title="Volume", overlaying="y", side="right"),
#         xaxis_rangeslider_visible=False,
#         height=500,
#     )

#     # === 2. EMA Chart ===
#     ema_fig = go.Figure()
#     ema_fig.add_trace(
#         go.Scatter(
#             x=df["timestamp"], y=df["close"], name="Price", line=dict(color="blue")
#         )
#     )
#     ema_fig.add_trace(
#         go.Scatter(x=df["timestamp"], y=ema, name="EMA", line=dict(color="orange"))
#     )
#     ema_fig.update_layout(title="EMA vs Price", height=400)

#     # === 3. RSI Chart ===
#     rsi_fig = go.Figure()
#     rsi_fig.add_trace(
#         go.Scatter(x=df["timestamp"], y=rsi, name="RSI", line=dict(color="purple"))
#     )
#     rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
#     rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
#     rsi_fig.update_layout(title="Relative Strength Index", height=300)

#     return signal_div, candle_fig, ema_fig, rsi_fig

