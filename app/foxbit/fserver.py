import asyncio
import foxbit
import db
from scopes import *

class FServer(object):
    def __init__(self, buffer):
        self.__foxbitClient = foxbit.Foxbit()
        self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 600
        self.__taxProfit = 0.05
        self.__managerBuffer = buffer

    async def listen(self):
        while True:
            currency_value_response = await self.__getCurrencyValue()
            bid = currency_value_response["Bid"]
            ask = currency_value_response["Ask"]

            trades_open = self.__getOpenTrades(bid/(1.0 + self.__taxProfit))

            if len(trades_open) > 0:
                self.__schedule_sells(currency_value_response, trades_open)
            
            wallets = Wallets.need_relocation(ask)
            self.__schedule_bundle_relocations(wallets, ask)

            await asyncio.sleep(self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS)

    async def __getCurrencyValue(self):
        response = await self.__foxbitClient.getTickerHistory()
        
        return response["o"]

    def __getOpenTrades(self, less_than):
        sql_query = "SELECT t.id " \
                  + "FROM trades AS t, orders AS o " \
                  + "WHERE t.order_sold_id IS NULL " \
                  + "AND o.ask < " + str(less_than) + " " \
                  + "AND t.order_bought_id = o.id"

        return db.manual(sql_query)
    
    def __schedule_sells(self, currencyValue, trades):
        order_id = db.insert("orders", ["ask", "bid"], [currencyValue["Ask"], currencyValue["Bid"]])[0][0]

        for trade in trades:
            self.__schedule_sell(trade[0], order_id)


    def __schedule_sell(self, trade_id, order_id):
        request = {
            "from": "foxbit",
            "data": {
                "operation": "sell_trade",
                "trade_id": trade_id,
                "order_id": order_id 
            }
        }

        self.__managerBuffer.push(request) 
    
    def __schedule_bundle_relocations(self, wallets, ask):
        for wallet in wallets:
            self.__schedule_relocation(wallet, ask)
    
    def __schedule_relocation(self, wallet, ask):
        if wallet.canRelocate(ask) == False:
            return None

        request = {
            "from": "foxbit",
            "data": {
                "operation": "wallet_relocation",
                "wallet_id": wallet.id(),
                "ask": ask
            }
        }

        self.__managerBuffer.push(request)

