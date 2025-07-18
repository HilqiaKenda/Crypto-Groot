from django.core.management.base import BaseCommand
import asyncio, json
import pandas as pd, websockets
from crypto_app.indicators import *

live_candles = pd.DataFrame(columns=['timestamp','open','high','low','close','volume'])

async def binance_ws(symbol, interval):
    uri = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"
    global live_candles
    async with websockets.connect(uri) as ws:
        while True:
            msg = await ws.recv()
            k = json.loads(msg)['k']
            if k['x']:
                row = {'timestamp': pd.to_datetime(k['t'], unit='ms'),
                       'open': float(k['o']), 'high': float(k['h']),
                       'low': float(k['l']), 'close': float(k['c']),
                       'volume': float(k['v'])}
                live_candles = pd.concat([live_candles, pd.DataFrame([row])]).tail(500).reset_index(drop=True)
            await asyncio.sleep(1)

class Command(BaseCommand):
    help = "Start Binance websocket feed"

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(binance_ws("btcusdt","1m"))
