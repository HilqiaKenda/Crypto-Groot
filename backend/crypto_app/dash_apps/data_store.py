import pandas as pd

# Shared across all modules
live_candles = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
