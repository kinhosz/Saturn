import hashlib, hmac
import os
import requests
import time
from datetime import datetime, timezone
from .throttle import throttle

class Foxbit(object):
  def __init__(self):
    self._domain = 'https://api.foxbit.com.br'
    self._resource_prefix = '/rest/v3'

  def _buildQuery(self, **params):
    query = ''
    for k, v in params.items():
      if v:
        query += '?' if query == '' else '&'
        query += "{}={}".format(k, v)
    return query

  def _buildHeaders(self, method, path, query):
    api_secret = os.getenv('FOXBIT_API_SECRET')

    timestamp = str(int(time.time() * 1000))
    preHash = f"{timestamp}{method.upper()}{self._resource_prefix}{path}{query}"
    print(preHash)
    signature = hmac.new(api_secret.encode(), preHash.encode(), hashlib.sha256).hexdigest()

    return {
      'X-FB-ACCESS-KEY': os.getenv('FOXBIT_API_KEY'),
      'X-FB-ACCESS-TIMESTAMP': timestamp,
      'X-FB-ACCESS-SIGNATURE': signature,
    }

  async def _request(self, method, path, auth=False, **params):
    query = self._buildQuery(**params)
    headers = None
    if auth:
      headers = self._buildHeaders(method, path, query)

    url = self._domain + self._resource_prefix + path + query
    response = requests.request(method, url, headers=headers)
    data = None

    if response.status_code != 500:
      data = response.json()
  
    return data, response.status_code

  @throttle
  async def getCandlesticks(self, market_symbol, interval, start_time=None, end_time=None, limit=None):
    path = "/markets/{market_symbol}/candlesticks".format(market_symbol=market_symbol)
    raw_candlesticks, code = await self._request(
      method='GET', path=path, interval=interval, start_time=start_time, end_time=end_time, limit=limit
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

  @throttle
  async def getMe(self):
    userInfo, code = await self._request(method='GET', path='/me', auth=True)
    if code != 200:
      return {}

    return userInfo
