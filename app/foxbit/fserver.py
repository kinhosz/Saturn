import asyncio
import foxbit
import db

# for seach21
import requests
import json
import time

class FServer(object):
    def __init__(self, buffer):
        self.__foxbitClient = foxbit.Foxbit()
        self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 600
        self.__taxProfit = 0.05
        self.__managerBuffer = buffer

    def findPalindrome(self, pi, start):
        sz = len(pi)
        DIG = 21

        answer = ""

        for i in range(0, sz - DIG + 1):
            palindrome = True
            for j in range(0, DIG//2):
                if pi[j + i] != pi[i + DIG - 1 - j]:
                    palindrome = False
                    break

            if palindrome == False:
                continue

            number = ""
            for j in range(0, DIG):
                number += pi[i + j]

            answer += number + "/"

        if answer != "":
            answer += "?"
            answer += str(start)
        
        return answer


    async def search21(self):
        f = open('start.txt', 'r')
        start = int(f.read())
        f.close()

        txt = "starting with " + str(start)
        self.__sendMessageToTelegram(txt, "log")
        await asyncio.sleep(10)

        DIGITS = 1000
        REQUESTS_TO_UPDATE = 10000
        request_count = 0
        old_partial = ""
        new_partial = ""

        tstart = time.time()

        while 1:
            successful = False
            while successful == False:
                url = "https://api.pi.delivery/v1/pi?start=" + str(start) + "&numberOfDigits=" + str(DIGITS)
                response = requests.get(url)
                print(response.status_code)

                if response.status_code == 200:
                    raw = response.content.decode("utf-8")

                    if "content" in raw:
                        data = json.loads(raw)
                        new_partial += data["content"]
                        successful = True

            request_count += 1

            if request_count == REQUESTS_TO_UPDATE:
                fullpartial = old_partial + new_partial
                answer = self.findPalindrome(fullpartial, start - DIGITS)
                old_partial = new_partial
                new_partial = ""

                if answer != "":
                    self.__sendMessageToTelegram(answer, "found")

                tend = time.time()
                avg_ping = (tend - tstart)/REQUESTS_TO_UPDATE
                tstart = time.time()

                request_count = 0
                f = open('start.txt', 'w')
                txt = str(start - DIGITS)
                f.write(txt)
                f.close()

                txt += " with ping = " + str(int(avg_ping * 1000)) + "ms"
                self.__sendMessageToTelegram(txt, "log")
                await asyncio.sleep(10)
            
            start += DIGITS

    async def listen(self):
        while True:
            currency_value_response = await self.__getCurrencyValue()
            bid = currency_value_response["Bid"]

            trades_open = self.__getOpenTrades(bid/(1.0 + self.__taxProfit))

            if len(trades_open) > 0:
                self.__schedule_sells(currency_value_response, trades_open)

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

    def __sendMessageToTelegram(self, message, type):
        if type == "log":
            request = {
                "from": "search21",
                "data": {
                    "log": message
                }
            }
        else:
            request = {
                "from": "search21",
                "data": {
                    "found": message
                }
            }
        
        self.__managerBuffer.push(request)
        
