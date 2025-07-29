from collections import defaultdict
import pandas as pd



"""Shared across all modules Global dictionary to store candles for each symbol"""
live_candles = defaultdict(lambda: pd.DataFrame(columns=[
    'timestamp', 'open', 'high', 'low', 'close', 'volume'
]))



"""Top 50 trading symbols on Binance (USDT pairs)"""
SYMBOLS = [
    'btcusdt', 'ethusdt', 'bnbusdt', 'solusdt', 'adausdt', 'xrpusdt', 'dogeusdt',
    'dotusdt', 'maticusdt', 'ltcusdt', 'bchusdt', 'uniusdt', 'linkusdt', 'trxusdt',
    'avaxusdt', 'xlmusdt', 'nearusdt', 'filusdt', 'atomusdt', 'etcusdt', 'vetusdt',
    'apeusdt', 'egldusdt', 'sandusdt', 'manausdt', 'icpusdt', 'ftmusdt', 'hbarusdt',
    'algousdt', 'thetausdt', 'xtzusdt', 'aaveusdt', 'chzusdt', 'enjusdt', 'runeusdt',
    'crvusdt', 'oneusdt', 'zecusdt', 'dashusdt', 'yfiusdt', 'compusdt', 'omgusdt',
    'sushiusdt', 'ankrusdt', 'lrcusdt', 'wavesusdt', 'zilusdt', 'balusdt', 'qtumusdt',
    'storjusdt'
]