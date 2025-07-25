from orm import Fields, Model

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from . import TypedEnv

class Order(Model):
    _table = 'orders'

    id = Fields.id()
    user_id = Fields.reference()
    foxbit_order_id = Fields.varchar()
    client_order_id = Fields.varchar()
    market_symbol = Fields.varchar()
    side = Fields.varchar()
    market_type = Fields.varchar()
    order_state = Fields.varchar()
    price = Fields.double()
    price_avg = Fields.double()
    quantity = Fields.double()
    quantity_executed = Fields.double()
    created_at = Fields.timestamp()
    trades_count = Fields.integer()
    remark = Fields.varchar()
    funds_received = Fields.double()
    fee_paid = Fields.double()
    post_only = Fields.boolean()
    time_in_force = Fields.varchar()
    cancellation_reason = Fields.integer()

    def update_from_foxbit(self, vals):
        self.foxbit_order_id = str(vals.get('id', self.foxbit_order_id))
        self.client_order_id = vals.get('client_order_id', self.client_order_id)
        self.market_symbol = vals.get('market_symbol', self.market_symbol)
        self.side = vals.get('side', self.side)
        self.market_type = vals.get('type', self.market_type)
        self.order_state = vals.get('state', self.order_state)
        self.price = vals.get('price', self.price)
        self.price_avg = vals.get('price_avg', self.price_avg)
        self.quantity = vals.get('quantity', self.quantity)
        self.quantity_executed = vals.get('quantity_executed', self.quantity_executed)
        self.created_at = vals.get('created_at', self.created_at)
        self.trades_count = vals.get('trades_count', self.trades_count)
        self.remark = vals.get('remark', self.remark)
        self.funds_received = vals.get('funds_received', self.funds_received)
        self.fee_paid = vals.get('fee_paid', self.fee_paid)
        self.cancellation_reason = vals.get('cancellation_reason', self.cancellation_reason)


    ################ Type Checking ######################
    @property
    def env(self) -> 'TypedEnv':
        return super().env

    @classmethod
    def find_by(cls, k, v) -> 'Order':
        return super().find_by(k, v)

    @classmethod
    def where(cls, **kwargs) -> List['Order']:
        return super().where(**kwargs)
