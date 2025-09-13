from datetime import datetime, timedelta
from orm import Fields, Model

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from . import TypedEnv

class Wallet(Model):
    _table = 'wallet'

    id = Fields.id()
    user_id = Fields.reference('res_user')
    lock_buy = Fields.boolean()
    lock_sell = Fields.boolean()
    allocation_percentage = Fields.double()
    percentage_to_sell = Fields.double()
    buy_window = Fields.integer()

    def cash_holding(self):
        return self.env['holding'].where(wallet_id=[self.id], base_symbol=['BRL'])[0]

    def invested_amount(self):
        holdings = self.env['holding'].where(wallet_id=[self.id])
        trades = self.env['trade'].where(user_id=[self.user_id.id], order_state=['ACTIVE', 'PARTIALLY_FILLED'])
        amount = 0.0
        for holding in holdings:
            if holding.base_symbol == 'BRL':
                amount += holding.amount
            elif holding.quote_symbol == 'BRL':
                amount += holding.price

        for trade in trades:
            amount += trade.quantity * trade.price + trade.quantity_executed * trade.price_avg

        return amount

    def cash_amount(self):
        holding = self.cash_holding()
        return holding.amount

    def buy_trade_amount(self):
        return int(self.invested_amount() * self.allocation_percentage)

    def can_buy(self):
        if self.lock_buy:
            return False
        if self.buy_trade_amount() > self.cash_amount():
            return False
        last_buy_window = self._last_buy_date() + timedelta(minutes=self.buy_window)
        return last_buy_window < datetime.now()

    def _last_buy_date(self):
        trades = self.env['trade'].where(side=['BUY'], user_id=[self.user_id.id])
        last_date = datetime.fromisoformat('2000-01-01')
        for trade in trades:
            if not trade.created_at:
                trade.created_at = datetime.now()
            last_date = max(last_date, trade.created_at)
        return last_date


    ################ Type Checking ######################
    @property
    def env(self) -> 'TypedEnv':
        return super().env

    @classmethod
    def find_by(cls, k, v) -> 'Wallet':
        return super().find_by(k, v)

    @classmethod
    def where(cls, **kwargs) -> List['Wallet']:
        return super().where(**kwargs)
