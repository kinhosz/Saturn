def compact(hash):
    compacted_hash = {}
    for k, v in hash.items():
        if not v:
            continue
        if isinstance(v, dict):
            v = compact(v)
        compacted_hash[k] = v
    return compacted_hash

def price_by_volume(candlesticks):
    sum_t = 0.0
    volume = 0.0

    for candle in candlesticks:
        avg_price = (candle['highest_price'] + candle['lowest_price']) / 2.0
        avg_price *= candle['base_volume']
        volume += candle['base_volume']

        sum_t += avg_price

    return sum_t / volume
