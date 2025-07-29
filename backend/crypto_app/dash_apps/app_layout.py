from django_plotly_dash import DjangoDash
from dash import dcc, html
from .data_store import SYMBOLS


app = DjangoDash("MainIndicators")

DEFAULT_SYMBOL = "btcusdt"

app.layout = html.Div(
    style={'textAlign': 'center'},

    children=[
        
        html.H2("📊 Groot Trading Market Analyze Dashboard", style={'textAlign': 'center'}), 
        
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
                "marginLeft": "20px",  
                "textAlign": "left"
            }
        ),        
        
        dcc.Interval(id="main-update", interval=5000, n_intervals=0),
        
        html.Div(id="currency-name", 
            style={"fontSize": "22px", 
                        "fontWeight": "bold", 
                        "marginBottom": "10px", 
                        "marginLeft": "20px"
            }
        ),
        
        html.Div(id="current-price", 
            style={"fontSize": "18px", 
                        "fontWeight": "bold", 
                        "marginBottom": "10px", 
                        "marginLeft": "20px"
            }
        ),

        html.Div(id="current-rsi", 
            style={"fontSize": "18px", 
                        "fontWeight": "bold", 
                        "marginBottom": "20px", 
                        "marginLeft": "20px"
            }
        ),
        
        # Candlestick chart and volume
        html.Div(id="candlestick-container", style={"marginTop": "20px"}),
        
        # EMA vs Price chart
        dcc.Graph(id="ema-chart"),
        
        # RSI chart"""
        dcc.Graph(id="rsi-chart"),
    ]
)