import plotly.graph_objs as go



def ema_vs_price_chart(df, ema):
    """EMA vs Price Chart"""
    
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
        title_x=0.5,
        title_xanchor="center",
        height=400,
    )

    return ema_fig





def rsi_price(df, rsi):
    """RSI Chart"""
    rsi_fig = go.Figure()
    rsi_fig.add_trace(
        go.Scatter(x=df["timestamp"], y=rsi, name="RSI", line=dict(color="purple"))
    )
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
    rsi_fig.update_layout(
        title="Relative Strength Index",
        title_x=0.5,
        title_xanchor="center",
        height=300,
    )
    
    return rsi_fig