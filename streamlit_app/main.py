import streamlit as st
from indicators import *

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# Display prices and indicators
st.title("📊 Real-Time Market Dashboard")

# Example: Plot MACD
macd, signal = compute_macd(live_data)
fig, ax = plt.subplots()
ax.plot(macd, label="MACD")
ax.plot(signal, label="Signal")
st.pyplot(fig)

# Repeat for: RSI, Bollinger Bands, OBV, etc.
