import asyncio
from datetime import datetime
from .foxbit import Foxbit
from .constants import *

class FServer(object):
    def __init__(self):
        self._foxbit = Foxbit()
        self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 600

    async def listen(self):
        while True:
            price = await self._getCurrentPrice('btcbrl')
            print("bitcoin price:", price)

            await asyncio.sleep(self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS)

    async def _getCurrentPrice(self, market_symbol):
        candlesticks = await self._foxbit.getCandlesticks(
            market_symbol=market_symbol,
            interval="1m",
            limit=1
        )

        if len(candlesticks) == 0:
            return None

        return candlesticks[0]['close_price']

    async def _createOrderLimit(self, side, quantity, price):
        client_order_id = str(int(datetime.now().timestamp()))
        res = await self._foxbit.createOrderLimit(
            side=side, client_order_id=client_order_id, quantity=quantity, price=price
        )

        return res

    async def _getOrder(self, order_id):
        order = await self._foxbit.getOrder(order_id)
        return order
