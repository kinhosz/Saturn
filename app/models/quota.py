from orm import Fields, Model

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from . import TypedEnv

class Quota(Model):
    _table = 'quotas'

    id = Fields.id()
    user_id = Fields.reference()
    purchase_order_id = Fields.reference()
    quota_state = Fields.varchar()
    amount = Fields.double()
    price = Fields.double()
    created_at = Fields.timestamp()


    ################ Type Checking ######################
    @property
    def env(self) -> 'TypedEnv':
        return super().env

    @classmethod
    def find_by(cls, k, v) -> 'Quota':
        return super().find_by(k, v)

    @classmethod
    def where(cls, **kwargs) -> List['Quota']:
        return super().where(**kwargs)
