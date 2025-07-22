from app.models import Order, Quota
from app.foxbit import FServer

from tests import float_compare
from tests import common

def base_order() -> Order:
    order = Order()
    order.client_order_id = '123456'
    order.market_symbol = 'btcbrl'
    order.side = 'BUY'
    order.market_type = 'LIMIT'
    order.order_state = 'DRAFT'

    return order

def test_quotas_creation(db_connection):
    """ Test if the quotas has been created when the purchase
        order is executed """
    user = common()
    fserver = FServer()

    quotas = Quota.where(quota_state=['ACTIVE'])
    assert len(quotas) == 0, "No quotas at this point"

    # Purchase order Filled
    order1 = base_order()
    order1.user_id = user.id
    order1.side = 'BUY'
    order1.quantity_executed = 1.0
    order1.fee_paid = 0.005
    order1.price_avg = 100000.0
    order1.quantity = 0.0
    order1.price = 95000.0
    order1.order_state = 'FILLED'
    order1.save()

    fserver._refund_order(order1)
    quotas = Quota.where(quota_state=['ACTIVE'])
    assert len(quotas) == 1, "A filled order must create a new quota"

    # Purchase order Partially Cancelled
    order2 = base_order()
    order2.user_id = user.id
    order2.side = 'BUY'
    order2.quantity_executed = 0.5
    order2.fee_paid = 0.0025
    order2.price_avg = 100000.0
    order2.quantity = 0.5
    order2.price = 95000.0
    order2.order_state = 'PARTIALLY_CANCELED'
    order2.save()

    fserver._refund_order(order2)
    quotas = Quota.where(quota_state=['ACTIVE'])
    assert len(quotas) == 2, "A partially canceled order must create a new quota"

    # Purchase Order Canceled
    order3 = base_order()
    order3.user_id = user.id
    order3.side = 'BUY'
    order3.quantity_executed = 0.0
    order3.fee_paid = 0.0
    order3.price_avg = 0.0
    order3.quantity = 1.0
    order3.price = 95000.0
    order3.order_state = 'CANCELED'
    order3.save()

    fserver._refund_order(order3)
    quotas = Quota.where(quota_state=['ACTIVE'])
    assert len(quotas) == 2, "A canceled order must not create a new quota"

    # Sale Order Filled
    order4 = base_order()
    order4.user_id = user.id
    order4.side = 'SELL'
    order4.quantity_executed = 1.0
    order4.fee_paid = 0.005
    order4.price_avg = 100000.0
    order4.quantity = 0.0
    order4.price = 95000.0
    order4.order_state = 'FILLED'
    order4.save()

    fserver._refund_order(order4)
    quotas = Quota.where(quota_state=['ACTIVE'])
    assert len(quotas) == 2, "A Sale Order must not create a new quota"

    for quota in quotas:
        assert quota.purchase_order_id in [order1.id, order2.id], "The purchase_order_id must be set"

        if quota.purchase_order_id == order1.id:
            assert float_compare(quota.amount, order1.quantity_executed - order1.fee_paid) == 0, \
                "The quota's amount must be the same of the executed quantity for an order, excluding the fee paid"
            assert float_compare(quota.price, order1.price_avg) == 1, "The quota price must be higher than the average order price"

        if quota.purchase_order_id == order2.id:
            assert float_compare(quota.amount, order2.quantity_executed - order2.fee_paid) == 0, \
                "The quota's amount must be the same of the executed quantity for an order, excluding the fee paid"
            assert float_compare(quota.price, order2.price_avg) == 1, "The quota price must be higher than the average order price"
