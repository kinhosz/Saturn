from .holding import Holding
from .deposit import Deposit
from .wallet import Wallet
from .trade import Trade
from .quota import Quota
from .user import User

from orm import Env, Model
from typing import overload, Literal

class TypedEnv(Env):
    @overload
    def __getitem__(self, name: Literal["holding"]) -> Holding: ...

    @overload
    def __getitem__(self, name: Literal["deposit"]) -> Deposit: ...

    @overload
    def __getitem__(self, name: Literal["wallet"]) -> Wallet: ...

    @overload
    def __getitem__(self, name: Literal["trade"]) -> Trade: ...

    @overload
    def __getitem__(self, name: Literal["quota"]) -> Quota: ...

    @overload
    def __getitem__(self, name: Literal["res_user"]) -> User: ...

    @overload
    def __getitem__(self, name: str) -> object: ...

    def __getitem__(self, name: str):
        return super().__getitem__(name)


env = TypedEnv()
Model.set_env(env)