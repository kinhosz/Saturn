from datetime import datetime
from app.models import Balance, Order, Quota, User, Wallet

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

    brl_balance = Balance()
    brl_balance.user_id = user.id
    brl_balance.amount = 100000.0
    brl_balance.base_symbol = 'BRL'
    brl_balance.price = 1.0
    brl_balance.quote_symbol = 'BTC'
    brl_balance.save()

    btc_balance = Balance()
    btc_balance.user_id = user.id
    btc_balance.amount = 1.0
    btc_balance.base_symbol = 'BTC'
    btc_balance.price = 100000.0
    btc_balance.quote_symbol = 'BRL'
    btc_balance.save()

    return user

def create_quota(user_id, amount, price):
    order = Order()
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