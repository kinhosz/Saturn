from enum import Enum

MINIMUM_BTC_TRADING = 0.00000132

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

class DepositStage(Enum):
    CONFIRMED = 'CONFIRMED'
    PENDING = 'PENDING'
    CANCELLED = 'CANCELLED'
