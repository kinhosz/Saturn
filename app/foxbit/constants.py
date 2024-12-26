from enum import Enum

class RestMethod(Enum):
    GET = 'GET'
    POST = 'POST'

class OrderType(Enum):
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    INSTANT = 'INSTANT'
    STOP = 'STOP_MARKET'

class OrderSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'
