import asyncio
from datetime import datetime, timezone
from typing import List

from app.models import Balance, Order, TradingSetting, User

from .foxbit import Foxbit
from .constants import *
from .messages import *
from ..services import *

class FServer(object):
    def __init__(self):
        self._foxbit = Foxbit()
        self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 5 * 60

        self._telegram_buffer = None

    def setTelegramBuffer(self, buffer):
        self._telegram_buffer = buffer

    async def listen(self):
        while True:
            candlestick = await self._getCurrentPrice('btcbrl')
            if candlestick:
                highest_price = candlestick['highest_price']
                lowest_price = candlestick['lowest_price']
                for k, v in candlestick.items():
                    print(f"{k}: {v}")
                print(f"saturn spread: {highest_price - lowest_price}")
                print("--------------")

                if candlestick['number_of_trades'] > 5:
                    await self._perform_purchase(highest_price)
                    await self._perform_sale(lowest_price)

                await self._process_active_orders()

            await asyncio.sleep(self.__DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS)

    async def _getCurrentPrice(self, market_symbol):
        candlesticks = await self._foxbit.getCandlesticks(
            market_symbol=market_symbol,
            interval="5m",
            limit=1
        )

        if len(candlesticks) == 0:
            return None

        return candlesticks[0]

    async def _createOrderLimit(self, side, quantity, price):
        client_order_id = str(generate_numeric_uuid())
        res, code = await self._foxbit.createOrderLimit(
            side=side, client_order_id=client_order_id, quantity=quantity, price=price
        )

        return res, code

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

    def _lock_operations_for_security(self, user_id, data, code):
        user = User(user_id)
        ts = TradingSetting.find_by('user_id', user.id)
        ts.lock_buy = True
        ts.lock_sell = True
        ts.save()

        self._telegram_buffer.push({
            'from': 'foxbit',
            'data': {
                'id': user.telegram_chat_id,
                'message': lock_for_security(data, code)
            }
        })

    async def _handle_executed_orders(self, executed_orders, side):
        for order_json in executed_orders:
            user = User(order_json['user_id'])
            data, code = await self._foxbit.getOrder(order_json['foxbit_order_id'])
            if code != 200:
                self._lock_operations_for_security(user.id, data, code)
                continue
            order = Order()
            order.update_from_foxbit(data)
            order.order_state = 'ACTIVE'
            order.user_id = order_json['user_id']
            order.save()

            balance = Balance(order_json['balance_id'])
            balance.amount -= order_json['partial_amount']
            balance.price -= order_json['partial_price']
            balance.save()

            trading_setting = TradingSetting.find_by('user_id', order.user_id)
            if side == 'BUY':
                trading_setting.exchange_count += 1 # Amplifier
            else:
                trading_setting.exchange_count -= 1 # Amplifier
            trading_setting.save()

            self._telegram_buffer.push({
                'from': 'foxbit',
                'data': {
                    'id': user.telegram_chat_id,
                    'message': order_executed(side, order.quantity + order.quantity_executed, order.price)
                }
            })

    async def _perform_purchase(self, price):
        executed_orders = await self._execute_purchase_orders(price)
        await self._handle_executed_orders(executed_orders, 'BUY')

    async def _execute_sale_orders(self, price):
        sellable_balances = find_sellable_balances(price, MINIMUM_BTC_TRADING)
        executed_orders = []
        for balance in sellable_balances:
            quantity = balance['partial_amount']
            res, code = await self._createOrderLimit(OrderSide.SELL.value, quantity, price)
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

    async def _perform_sale(self, price):
        executed_orders = await self._execute_sale_orders(price)
        await self._handle_executed_orders(executed_orders, 'SELL')

    def _notify_order_done(self, order: Order):
        user = User(order.user_id)
        if order.order_state == 'CANCELED':
            msg = order_cancelled(order.quantity, order.price_avg, order.cancellation_reason)
        elif order.order_state == 'FILLED':
            msg = order_filled(order.quantity_executed, order.price_avg)
        elif order.order_state == 'PARTIALLY_CANCELED':
            msg = order_partially_cancelled(order.quantity, order.quantity_executed, order.price_avg, order.cancellation_reason)
        else:
            return None

        self._telegram_buffer.push({
            'from': 'foxbit',
            'data': {
                'id': user.telegram_chat_id,
                'message': msg
            }
        })

    def _refund_order(self, order: Order):
        if order.side == 'BUY':
            btc_amount = order.quantity_executed - order.fee_paid
            btc_amount_cost = order.quantity_executed * order.price_avg # taxes included
            brl_amount = order.quantity * order.price
            brl_amount_cost = order.quantity
        elif order.side == 'SELL':
            brl_amount = order.quantity_executed * order.price_avg - order.fee_paid
            brl_amount_cost = order.quantity_executed # taxes included
            btc_amount = order.quantity
            btc_amount_cost = order.quantity * order.price

        balances: List[Balance] = Balance.where(user_id = [order.user_id])
        for balance in balances:
            if balance.base_symbol == 'BTC' and balance.quote_symbol == 'BRL':
                balance.amount += btc_amount
                balance.price += btc_amount_cost
            elif balance.base_symbol == 'BRL' and balance.quote_symbol == 'BTC':
                balance.amount += brl_amount
                balance.price += brl_amount_cost
            else:
                continue

            balance.save()

    async def _process_active_orders(self):
        active_orders: List[Order] = Order.where(order_state=['PARTIALLY_FILLED', 'ACTIVE'])

        for order in active_orders:
            data, code = await self._foxbit.getOrder(order.foxbit_order_id)
            if code != 200:
                print(f"Data: {data}\nCode: {code}")
                continue
            order.update_from_foxbit(data)
            order.save()

            if order.order_state not in ['CANCELED', 'FILLED', 'PARTIALLY_CANCELED']:
                continue

            self._notify_order_done(order)
            self._refund_order(order)
