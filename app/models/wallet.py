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
    percentage_to_buy = Fields.double()
    percentage_to_sell = Fields.double()
    exchange_count = Fields.integer()


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
