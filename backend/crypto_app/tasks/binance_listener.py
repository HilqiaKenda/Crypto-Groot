import asyncio
import json
import pandas as pd
import websockets
import threading
from crypto_app.dash_apps.data_store import SYMBOLS, live_candles
from .fetch_initial_candles import fetch_initial_candles



def start_ws(symbols=SYMBOLS, interval="1m"):
    async def listen():
        stream_names = [f"{s}@kline_{interval}" for s in symbols]
        streams = "/".join(stream_names)
        uri = f"wss://stream.binance.com:9443/stream?streams={streams}"
        # uri = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"
        # uri = f"wss://stream.binance.com:9443/ws/{streams}"

        async with websockets.connect(uri) as websocket:
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)
                k = data['data']['k']
                symbol = data['data']['s'].lower()

                
                # Candle closed
                if k['x']:  
                    candle = {
                        'timestamp': pd.to_datetime(k['t'], unit='ms'),
                        'open': float(k['o']),
                        'high': float(k['h']),
                        'low': float(k['l']),
                        'close': float(k['c']),
                        'volume': float(k['v']),
                    }

                    df = live_candles[symbol]
                    new_df = pd.DataFrame([candle])
                    df = pd.concat([df, new_df], ignore_index=True).tail(500).reset_index(drop=True)
                    live_candles[symbol] = df


    """Fetch initial historical data first"""
    for sym in symbols:
        fetch_initial_candles(sym)


    """Start async loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen())


def start_ws_thread():
    thread = threading.Thread(target=start_ws, daemon=True)
    thread.start()


"""Call this from somewhere safe, or use Celery later"""
threading.Thread(target=start_ws).start()




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

