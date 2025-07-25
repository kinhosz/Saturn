from orm import Fields, Model

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from . import TypedEnv

class Holding(Model):
    _table = 'holding'

    id = Fields.id()
    user_id = Fields.reference()
    wallet_id = Fields.reference()
    amount = Fields.double()
    base_symbol = Fields.varchar()
    # TODO: Remove price and quote_symbol
    price = Fields.double()
    quote_symbol = Fields.varchar()


    ################ Type Checking ######################
    @property
    def env(self) -> 'TypedEnv':
        return super().env

    @classmethod
    def find_by(cls, k, v) -> 'Holding':
        return super().find_by(k, v)

    @classmethod
    def where(cls, **kwargs) -> List['Holding']:
        return super().where(**kwargs)