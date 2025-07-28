import pytest
from .common import common
from .utils import float_compare
from app.foxbit import FServer
from app.models import Trade, Wallet

@pytest.mark.asyncio
async def test_wallet(db_connection):
    user = common()
    wallet = Wallet.find_by('user_id', user.id)
    price = 100000.0
    fserver = FServer()

    assert float_compare(wallet.invested_amount(), 200000) == 0
    assert float_compare(wallet.cash_amount(), 100000) == 0

    await fserver._perform_purchase(price)
    trade = Trade.where(user_id=[user.id])[0]

    trade.order_state = 'FILLED'
    trade.quantity_executed += trade.quantity
    trade.quantity = 0.0
    trade.fee_paid = 0.01
    trade.price_avg = price
    trade.save()
    fserver._refund_order(trade)

    assert float_compare(wallet.invested_amount(), 200000) == 0
    assert float_compare(wallet.cash_amount(), 80000) == 0

    assert wallet.can_buy() == False
