from datetime import datetime
from app.models import Holding, Trade, Quota, User, Wallet

def common():
    user = User()
    user.active = True
    user.telegram_username = 'admin'
    user.telegram_chat_id = 123456
    user.save()

    trading = Wallet()
    trading.user_id = user.id
    trading.lock_buy = False
    trading.lock_sell = False
    trading.allocation_percentage = 0.1
    trading.percentage_to_buy = 0.99
    trading.percentage_to_sell = 1.01
    trading.exchange_count = 0
    trading.save()

    brl_holding = Holding()
    brl_holding.user_id = user.id
    brl_holding.amount = 100000.0
    brl_holding.base_symbol = 'BRL'
    brl_holding.price = 1.0
    brl_holding.quote_symbol = 'BTC'
    brl_holding.save()

    btc_holding = Holding()
    btc_holding.user_id = user.id
    btc_holding.amount = 1.0
    btc_holding.base_symbol = 'BTC'
    btc_holding.price = 100000.0
    btc_holding.quote_symbol = 'BRL'
    btc_holding.save()

    return user

def create_quota(user_id, amount, price):
    order = Trade()
    order.user_id = user_id
    # Mandatory fields
    order.client_order_id = '123456'
    order.market_symbol = 'btcbrl'
    order.side = 'BUY'
    order.market_type = 'LIMIT'
    order.order_state = 'DRAFT'
    order.save()

    quota = Quota()
    quota.amount = amount
    quota.price = price
    quota.purchase_order_id = order.id
    quota.user_id = user_id
    quota.quota_state = 'ACTIVE'
    quota.created_at = datetime.today()
    quota.save()

    return quota