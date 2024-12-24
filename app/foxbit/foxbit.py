import requests
from datetime import datetime, timezone
from .throttle import throttle

class Foxbit(object):
  def __init__(self):
    self._base_url = 'https://api.foxbit.com.br/rest/v3'
    self._last_request = {}

  async def _get(self, path, **params):
    query = ''
    for k, v in params.items():
      if v:
        query += '?' if query == '' else '&'
        query += "{}={}".format(k, v)

    url = self._base_url + path + query
    response = requests.get(url)
    data = None

    if response.status_code == 200:
      data = response.json()
  
    return data, response.status_code

  @throttle
  async def getCandlesticks(self, market_symbol, interval, start_time=None, end_time=None, limit=None):
    path = "/markets/{market_symbol}/candlesticks".format(market_symbol=market_symbol)
    raw_candlesticks, code = await self._get(
      path=path, interval=interval, start_time=start_time, end_time=end_time, limit=limit
    )

    if code != 200:
      return []

    candlesticks = []
    for candle in raw_candlesticks:
      candlesticks.append({
        'open_date_time':  datetime.fromtimestamp(int(candle[0]) / 1000, tz=timezone.utc),
        'open_price': float(candle[1]),
        'highest_price': float(candle[2]),
        'lowest_price': float(candle[3]),
        'close_price': float(candle[4]),
        'close_date_time': datetime.fromtimestamp(int(candle[5]) / 1000, tz=timezone.utc),
        'base_volume': float(candle[6]),
        'quote_volume': float(candle[7]),
        'number_of_trades': int(candle[8]),
        'taker_buy_base_volume': float(candle[9]),
        'taker_buy_quote_volume': float(candle[10])
      })

    return candlesticks
