import asyncio
import foxbit

class FServer(object):
    def __init__(self, buffer):
        self._foxbit = foxbit.Foxbit()
        self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 60

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
