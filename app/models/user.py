from orm import Fields, Model

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from . import TypedEnv

class User(Model):
    _table = 'users'

    id = Fields.id()
    telegram_chat_id = Fields.integer()
    telegram_username = Fields.varchar()
    active = Fields.boolean()


    ################ Type Checking ######################
    @property
    def env(self) -> 'TypedEnv':
        return super().env

    @classmethod
    def find_by(cls, k, v) -> 'User':
        return super().find_by(k, v)

    @classmethod
    def where(cls, **kwargs) -> List['User']:
        return super().where(**kwargs)
