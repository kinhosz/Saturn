from orm import Fields, Model

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from . import TypedEnv

class Deposit(Model):
    _table = 'deposit'

    id = Fields.id()
    user_id = Fields.reference('res_user')
    amount = Fields.double()
    stage = Fields.varchar()


    ################ Type Checking ######################
    @property
    def env(self) -> 'TypedEnv':
        return super().env

    @classmethod
    def find_by(cls, k, v) -> 'Deposit':
        return super().find_by(k, v)

    @classmethod
    def where(cls, **kwargs) -> List['Deposit']:
        return super().where(**kwargs)
