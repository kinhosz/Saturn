import hashlib, hmac
import json
import os
import requests
import time
import uuid
from datetime import datetime, timezone
from .constants import *
from .throttle import throttle
from .utils import *

class Foxbit(object):
  def __init__(self):
    self._domain = 'https://api.foxbit.com.br'
    self._resource_prefix = '/rest/v3'

  def _buildQuery(self, **params):
    params = compact(params)
    query = ''
    for k, v in params.items():
      query += '&' if query != '' else ''
      query += "{}={}".format(k, v)
    return query

  def _buildHeaders(self, method, path, queryString, body):
    api_secret = os.getenv('FOXBIT_API_SECRET')

    timestamp = str(int(time.time() * 1000))
    raw_body = ''
    if body:
      raw_body = json.dumps(compact(body))

    preHash = f"{timestamp}{method.value.upper()}{self._resource_prefix}{path}{queryString}{raw_body}"
    signature = hmac.new(api_secret.encode(), preHash.encode(), hashlib.sha256).hexdigest()

    headers = {
      'X-FB-ACCESS-KEY': os.getenv('FOXBIT_API_KEY'),
      'X-FB-ACCESS-TIMESTAMP': timestamp,
      'X-FB-ACCESS-SIGNATURE': signature,
    }

    if method == RestMethod.POST:
      headers['X-Idempotent'] = str(uuid.uuid4()).lower()

    return headers

  async def _request(self, method, path, auth=True, body=None, **params):
    if body:
      body = compact(body)

    query = self._buildQuery(**params)
    headers = None
    if auth:
      headers = self._buildHeaders(method, path, query, body)

    url = self._domain + self._resource_prefix + path
    response = requests.request(method.value, url, headers=headers, params=query, json=body)
    data = None

    if response.status_code != 500:
      data = response.json()
  
    return data, response.status_code

  @throttle
  async def getCandlesticks(self, market_symbol, interval, start_time=None, end_time=None, limit=None):
    path = "/markets/{market_symbol}/candlesticks".format(market_symbol=market_symbol)
    raw_candlesticks, code = await self._request(
      method=RestMethod.GET, path=path, interval=interval, start_time=start_time, end_time=end_time, limit=limit, auth=False
    )

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
    userInfo, code = await self._request(method=RestMethod.GET, path='/me')
    return userInfo

  @throttle
  async def getTradingFees(self):
    fees, code = await self._request(method=RestMethod.GET, path='/me/fees/trading')
    return fees

  @throttle
  async def createOrderLimit(self, side, client_order_id, quantity, price, market_symbol='btcbrl', post_only=None, time_in_force=None):
    body = {
      'side': str(side),
      'type': OrderType.LIMIT.value,
      'market_symbol': market_symbol,
      'client_order_id': client_order_id,
      'remark': "Order Created by Saturn. Don't modify this order.",
      'quantity': "{:.16f}".format(quantity),
      'price': "{:.16f}".format(price),
      'post_only': post_only,
      'time_in_force': time_in_force,
    }
    response, code = await self._request(method=RestMethod.POST, path='/orders', body=body)

    return response, code

  @throttle
  async def getOrder(self, order_id):
    path = "/orders/by-order-id/{id}".format(id=order_id)
    response, code = await self._request(method=RestMethod.GET, path=path)

    str_to_float = ['price', 'price_avg', 'quantity', 'quantity_executed', 'funds_received', 'fee_paid']
    for k in str_to_float:
      response[k] = float(response[k]) if response.get(k, False) else None
    response['created_at'] = datetime.fromisoformat(response['created_at'].replace("Z", "+00:00"))
    response['id'] = int(response['id'])

    return response, code

  @throttle
  async def listOrders(self, start_time=None, end_time=None, page_size=None, page=None, market_symbol=None, side=None, state=None):
    path = '/orders'
    response, code = await self._request(
      method=RestMethod.GET, path=path, start_time=start_time, end_time=end_time, page_size=page_size,
      page=page, market_symbol=market_symbol, side=side, state=state
    )

    return response, code
