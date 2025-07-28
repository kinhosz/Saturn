import pytest
from datetime import timedelta
from .common import common
from app.foxbit import FServer
from app.models import Trade

@pytest.mark.asyncio
async def test_perform_purchase(db_connection):
    user = common()

    fserver = FServer()
    price = 100000

    trades = Trade.where(user_id=[user.id])
    assert len(trades) == 0, 'No trades at this point'

    await fserver._perform_purchase(price)

    trades = Trade.where(user_id=[user.id])
    assert len(trades) == 1, 'Trade has been created'

    # New purchase are blocked due window period
    await fserver._perform_purchase(price)

    trades = Trade.where(user_id=[user.id])
    assert len(trades) == 1, 'Trades must not be created'

    # Now, since the 2 days after the last trade. We are able to buy a new one
    trades[0].created_at -= timedelta(days=2)
    trades[0].save()

    await fserver._perform_purchase(price)

    trades = Trade.where(user_id=[user.id])
    assert len(trades) == 2, 'A new trade has been created'
