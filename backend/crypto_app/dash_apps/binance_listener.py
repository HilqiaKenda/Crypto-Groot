import asyncio
import json
import threading
import pandas as pd
import requests
import websockets
from datetime import datetime
from collections import defaultdict

# Global dictionary to store candles for each symbol
symbol_candles = defaultdict(lambda: pd.DataFrame(columns=[
    'timestamp', 'open', 'high', 'low', 'close', 'volume'
]))

# Top 50 trading symbols on Binance (USDT pairs)
symbols = [
    'btcusdt', 'ethusdt', 'bnbusdt', 'solusdt', 'adausdt', 'xrpusdt', 'dogeusdt',
    'dotusdt', 'maticusdt', 'ltcusdt', 'bchusdt', 'uniusdt', 'linkusdt', 'trxusdt',
    'avaxusdt', 'xlmusdt', 'nearusdt', 'filusdt', 'atomusdt', 'etcusdt', 'vetusdt',
    'apeusdt', 'egldusdt', 'sandusdt', 'manausdt', 'icpusdt', 'ftmusdt', 'hbarusdt',
    'algousdt', 'thetausdt', 'xtzusdt', 'aaveusdt', 'chzusdt', 'enjusdt', 'runeusdt',
    'crvusdt', 'oneusdt', 'zecusdt', 'dashusdt', 'yfiusdt', 'compusdt', 'omgusdt',
    'sushiusdt', 'ankrusdt', 'lrcusdt', 'wavesusdt', 'zilusdt', 'balusdt', 'qtumusdt',
    'storjusdt'
]

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

        symbol_candles[symbol] = pd.DataFrame(data)
        print(f"Fetched historical candles for {symbol.upper()}")
    except Exception as e:
        print(f"Failed to fetch initial candles for {symbol.upper()}: {e}")

def start_ws(symbols=symbols, interval="1m"):
    async def listen():
        stream_names = [f"{s}@kline_{interval}" for s in symbols]
        streams = "/".join(stream_names)
        uri = f"wss://stream.binance.com:9443/stream?streams={streams}"
        print(f"Connecting to Binance WebSocket for {len(symbols)} symbols...")

        async with websockets.connect(uri) as websocket:
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)
                k = data['data']['k']
                symbol = data['data']['s'].lower()

                if k['x']:  # Candle closed
                    candle = {
                        'timestamp': pd.to_datetime(k['t'], unit='ms'),
                        'open': float(k['o']),
                        'high': float(k['h']),
                        'low': float(k['l']),
                        'close': float(k['c']),
                        'volume': float(k['v']),
                    }

                    df = symbol_candles[symbol]
                    new_df = pd.DataFrame([candle])
                    df = pd.concat([df, new_df], ignore_index=True).tail(500).reset_index(drop=True)
                    symbol_candles[symbol] = df

                    print(f"[{symbol.upper()}] {candle['timestamp']} Close: {candle['close']}")

    # Fetch initial historical data first
    for sym in symbols:
        fetch_initial_candles(sym)

    # Start async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen())

def start_ws_thread():
    thread = threading.Thread(target=start_ws, daemon=True)
    thread.start()


# import asyncio
# import json
# import pandas as pd
# import websockets
# import threading
# from datetime import datetime

# def start_ws(symbol="btcusdt", interval="1m"):
#     async def listen():
#         uri = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"
#         print(f"Connecting to Binance WebSocket for {symbol}...")

#         async with websockets.connect(uri) as websocket:
#             while True:
#                 msg = await websocket.recv()
#                 data = json.loads(msg)
#                 k = data['k']
#                 if k['x']:
#                     candle = {
#                         'timestamp': pd.to_datetime(k['t'], unit='ms'),
#                         'open': float(k['o']),
#                         'high': float(k['h']),
#                         'low': float(k['l']),
#                         'close': float(k['c']),
#                         'volume': float(k['v']),
#                     }
#                     new_df = pd.DataFrame([candle])
#                     live_candles.drop(live_candles.index, inplace=True)
#                     live_candles[:] = pd.concat([live_candles, new_df], ignore_index=True).tail(500).reset_index(drop=True)
#                     print("Updated candle:", candle)

#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(listen())

# def start_ws_thread():
#     thread = threading.Thread(target=start_ws, daemon=True)
#     thread.start()







# import asyncio
# import json
# import pandas as pd
# import websockets
# import threading
# from datetime import datetime

# # Store candles per symbol
# symbol_candles = {}

# # Pick your top 50 symbols (can be dynamic via Binance API too)
# symbols = [
#     'btcusdt', 'ethusdt', 'bnbusdt', 'solusdt', 'adausdt', 'xrpusdt', 'dogeusdt',
#     'dotusdt', 'maticusdt', 'ltcusdt', 'bchusdt', 'uniusdt', 'linkusdt', 'trxusdt',
#     'avaxusdt', 'xlmusdt', 'nearusdt', 'filusdt', 'atomusdt', 'etcusdt', 'vetusdt',
#     'apeusdt', 'egldusdt', 'sandusdt', 'manausdt', 'icpusdt', 'ftmusdt', 'hbarusdt',
#     'algousdt', 'thetausdt', 'xtzusdt', 'aaveusdt', 'chzusdt', 'enjusdt', 'runeusdt',
#     'crvusdt', 'oneusdt', 'zecusdt', 'dashusdt', 'yfiusdt', 'compusdt', 'omgusdt',
#     'sushiusdt', 'ankrusdt', 'lrcusdt', 'wavesusdt', 'zilusdt', 'balusdt', 'qtumusdt',
#     'storjusdt'
# ]

# def start_ws(symbols=symbols, interval="1m"):
#     async def listen():
#         stream_names = [f"{s}@kline_{interval}" for s in symbols]
#         streams = "/".join(stream_names)
#         uri = f"wss://stream.binance.com:9443/stream?streams={streams}"
#         print(f"Connecting to Binance WebSocket for {len(symbols)} symbols...")

#         async with websockets.connect(uri) as websocket:
#             while True:
#                 msg = await websocket.recv()
#                 data = json.loads(msg)
#                 k = data['data']['k']
#                 symbol = data['data']['s'].lower()

#                 if k['x']:  # Only process closed candles
#                     candle = {
#                         'timestamp': pd.to_datetime(k['t'], unit='ms'),
#                         'open': float(k['o']),
#                         'high': float(k['h']),
#                         'low': float(k['l']),
#                         'close': float(k['c']),
#                         'volume': float(k['v']),
#                     }

#                     if symbol not in symbol_candles:
#                         symbol_candles[symbol] = pd.DataFrame(columns=[
#                             'timestamp', 'open', 'high', 'low', 'close', 'volume'
#                         ])

#                     df = symbol_candles[symbol]
#                     new_df = pd.DataFrame([candle])
#                     df = pd.concat([df, new_df], ignore_index=True).tail(500).reset_index(drop=True)
#                     symbol_candles[symbol] = df

#                     print(f"Updated {symbol.upper()} candle at {candle['timestamp']}")

#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(listen())

# def start_ws_thread():
#     thread = threading.Thread(target=start_ws, daemon=True)
#     thread.start()




# import asyncio
# import json
# import pandas as pd
# import websockets
# import threading
# from datetime import datetime

# live_candles = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# def start_ws(symbol="btcusdt", interval="1m"):
#     async def listen():
#         uri = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"
#         global live_candles

#         async with websockets.connect(uri) as websocket:
#             while True:
#                 msg = await websocket.recv()
#                 data = json.loads(msg)
#                 k = data['k']
#                 if k['x']:
#                     candle = {
#                         'timestamp': pd.to_datetime(k['t'], unit='ms'),
#                         'open': float(k['o']),
#                         'high': float(k['h']),
#                         'low': float(k['l']),
#                         'close': float(k['c']),
#                         'volume': float(k['v']),
#                     }
#                     new_df = pd.DataFrame([candle])
#                     live_candles = pd.concat([live_candles, new_df], ignore_index=True).tail(500).reset_index(drop=True)

#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(listen())

# # Call this from somewhere safe, or use Celery later
# threading.Thread(target=start_ws).start()
