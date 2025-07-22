from orm import Fields, Model

class Wallet(Model):
    _table = 'wallet'

    id = Fields.id()
    user_id = Fields.reference()
    lock_buy = Fields.boolean()
    lock_sell = Fields.boolean()
    allocation_percentage = Fields.double()
    percentage_to_buy = Fields.double()
    percentage_to_sell = Fields.double()
    exchange_count = Fields.integer()
