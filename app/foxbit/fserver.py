import asyncio
import foxbit

class FServer(object):
    def __init__(self):
        self.__foxbitClient = foxbit.Foxbit()
        self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 600
        self.__taxProfit = 0.1

    async def listen(self):
        while True:
            response = await self.__getCurrencyValue()
            bid = response["Bid"]


            await asyncio.sleep(self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS)

    async def __getCurrencyValue(self):
        response = await self.__foxbitClient.getTickerHistory()
        
        return response["o"]