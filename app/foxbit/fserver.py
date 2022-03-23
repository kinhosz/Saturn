import asyncio
import foxbit
from db.query import *
from db.insert import *

class FServer(object):
    def __init__(self):
        self.__foxbitClient = foxbit.Foxbit()
        self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 600
        self.__taxProfit = 0.1

    async def listen(self):
        while True:
            currency_value_response = await self.__getCurrencyValue()
            bid = currency_value_response["Bid"]

            database_response = self.__getOpenTrades(bid/(1.0 + self.__taxProfit))

            if len(database_response) > 0:
                self.__perform_bundle_sells(currency_value_response, database_response)

            await asyncio.sleep(self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS)

    async def __getCurrencyValue(self):
        response = await self.__foxbitClient.getTickerHistory()
        
        return response["o"]

    def __getOpenTrades(self, less_than):
        sql_query = "SELECT t.id " \
                  + "FROM trades AS t, orders AS o " \
                  + "WHERE t.order_sold_id IS NULL " \
                  + "AND o.ask < " + str(less_than) + " " \
                  + "AND t.bought_order_id = o.id"

        return manual(sql_query)
    
    def __perform_bundle_sells(currencyValue, trades_open):
        order_id = insert("orders", ["ask", "bid"], [currencyValue["Ask"], currencyValue["Bid"]])
        
