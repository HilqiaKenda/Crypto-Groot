
from django.core.cache import cache

def save_to_cache(symbol, data):
    """ Save the candle data to Redis cache """
    cache_key = f"candle:{symbol}"
    
    # If data exists, append to the cache
    existing_data = cache.get(cache_key) or []
    existing_data.append(data)
    
    # Limit the number of candles stored in the cache (e.g., store only the last 500 candles)
    if len(existing_data) > 500:
        existing_data = existing_data[-500:]
    
    # Store the data back into the cache
    cache.set(cache_key, existing_data, timeout=None)  # Timeout=None makes it persistent in cache
