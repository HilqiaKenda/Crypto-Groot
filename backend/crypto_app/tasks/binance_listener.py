# dashboard/tasks/binance_listener.py

import asyncio
import json
import pandas as pd
import websockets
import threading
from datetime import datetime

live_candles = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

def start_ws(symbol="btcusdt", interval="1m"):
    async def listen():
        uri = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"
        global live_candles

        async with websockets.connect(uri) as websocket:
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)
                k = data['k']
                if k['x']:
                    candle = {
                        'timestamp': pd.to_datetime(k['t'], unit='ms'),
                        'open': float(k['o']),
                        'high': float(k['h']),
                        'low': float(k['l']),
                        'close': float(k['c']),
                        'volume': float(k['v']),
                    }
                    new_df = pd.DataFrame([candle])
                    live_candles = pd.concat([live_candles, new_df], ignore_index=True).tail(500).reset_index(drop=True)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen())

# Call this from somewhere safe, or use Celery later
threading.Thread(target=start_ws).start()
