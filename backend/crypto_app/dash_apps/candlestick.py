import plotly.graph_objs as go



def candlestick_with_volume_and_ema(df, symbol, ema):
    """Candlestick with Volume and EMA"""
    
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
        title_x=0.5,
        title_xanchor="center",
        yaxis=dict(title="Price"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
        xaxis_rangeslider_visible=False,
        height=500,
    )


    return candle_fig