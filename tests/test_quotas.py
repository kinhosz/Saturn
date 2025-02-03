from app.models import Balance, TradingSetting, User

def common():
    user = User()
    user.active = True
    user.telegram_username = 'admin'
    user.telegram_chat_id = 123456
    user.save()

    trading = TradingSetting()
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
    brl_balance.amount = 100.0
    brl_balance.base_symbol = 'BRL'
    brl_balance.save()

    btc_balance = Balance()
    btc_balance.user_id = user.id
    btc_balance.amount = 0.001
    btc_balance.base_symbol = 'BTC'
    btc_balance.save()

def test_quotas(db_connection):
    common()

    user = User.find_by('telegram_chat_id', 123456)
    assert user.telegram_username == 'admin'
    # TODO: Finish the tests
