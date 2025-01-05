import asyncio
from datetime import datetime, timezone
from .foxbit import Foxbit
from .constants import *
from .messages import *
from ..services import *

class FServer(object):
    def __init__(self):
        self._foxbit = Foxbit()
        self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 600

        self._telegram_buffer = None

    def setTelegramBuffer(self, buffer):
        self._telegram_buffer = buffer

    async def listen(self):
        while True:
            price = await self._getCurrentPrice('btcbrl')
            print("bitcoin price:", price)
            await self._perform_purchase(price)

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
        client_order_id = str(generate_numeric_uuid())
        res, code = await self._foxbit.createOrderLimit(
            side=side, client_order_id=client_order_id, quantity=quantity, price=price
        )

        return res, code

    async def _getOrder(self, order_id):
        order = await self._foxbit.getOrder(order_id)
        return order

    async def _execute_purchase_orders(self, price):
        buyable_balances = find_buyable_balances(price, MINIMUM_BTC_TRADING)
        executed_orders = []
        for balance in buyable_balances:
            quantity = balance['partial_amount'] / price
            res, code = await self._createOrderLimit(OrderSide.BUY.value, quantity, price)
            if code == 201:
                executed_orders.append({
                    'balance_id': balance['balance_id'],
                    'user_id': balance['user_id'],
                    'partial_price': balance['partial_price'],
                    'partial_amount': balance['partial_amount'],
                    'foxbit_order_id': str(res['id']),
                    'client_order_id': str(res['client_order_id'])
                })
            else:
                print("Order Cancelled.\nCode[{}].\nResponse: {}".format(code, res))

        return executed_orders

    async def _list_orders(self, start_time=None, end_time=None, order_side=None):
        if start_time:
            start_time = start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        if end_time:
            end_time = end_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        orders = []
        page = 1

        current_orders, code = await self._foxbit.listOrders(
            start_time=start_time, end_time=None, page_size=100, page=1, market_symbol='btcbrl', side=order_side
        )
        while code == 200 and len(current_orders['data']) > 0:
            orders += current_orders['data']
            page += 1
            current_orders, code = await self._foxbit.listOrders(
                start_time=start_time, end_time=None, page_size=100, page=page, market_symbol='btcbrl', side=order_side
            )

        return orders

    async def _perform_purchase(self, price):
        start_time = datetime.now()
        executed_orders = await self._execute_purchase_orders(price)
        if executed_orders == []:
            return None

        fully_orders = await self._list_orders(start_time=start_time, order_side=OrderSide.BUY.value)

        tmp_orders = {}
        for order in executed_orders:
            tmp_orders[order['foxbit_order_id']] = order
        for order in fully_orders:
            order.update(tmp_orders.get(order['id'], {}))
            order['order_state'] = 'ACTIVE'
            order['market_type'] = order['type']

        to_update = []
        for order in fully_orders:
            to_update.append({
                'balance_id': order['balance_id'],
                'partial_amount': -order['partial_amount'],
                'partial_price': -order['partial_price'] 
            })

        update_balances(to_update)
        write_orders(fully_orders)

        user_ids = [o['user_id'] for o in fully_orders]
        res = find_users(user_ids)
        user_by_id = {}
        for r in res:
            user_by_id[r['id']] = r

        for order in fully_orders:
            self._telegram_buffer.push({
                'from': 'foxbit',
                'data': {
                    'id': user_by_id[order['user_id']]['telegram_chat_id'],
                    'message': order_executed('BUY', order['quantity'], order['price'])
                }
            })
