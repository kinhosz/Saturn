import asyncio, time

# name: [requests, seconds]
_RATE_LIMIT = {
  'default': [300, 10],
  'getCandlesticks': [5, 2],
  'getMe': [1, 1],
  'getOrder': [30, 2],
  'getTradingFees': [1, 2],
  'listOrders': [30, 2],
}

_last_request = {}

def _getThrottleDelay(method):
  if method in _RATE_LIMIT.keys():
    return _RATE_LIMIT[method][1] / _RATE_LIMIT[method][0]  
  return _getThrottleDelay('default')

def throttle(func):
  async def wrapper(*args, **kwargs):
    if func.__name__ in _last_request.keys():
      curr_time = time.perf_counter()
      passed_time = curr_time - _last_request[func.__name__]
      delay = _getThrottleDelay(func.__name__)
      if passed_time < delay:
        await asyncio.sleep(delay - passed_time)

    res = await func(*args, **kwargs)

    _last_request[func.__name__] = time.perf_counter()
    return res
  return wrapper
