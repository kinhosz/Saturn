from orm import Fields, Model

class Balance(Model):
    _table = 'balances'

    id = Fields.id()
    user_id = Fields.reference()
    amount = Fields.double()
    base_symbol = Fields.varchar()
    price = Fields.double()
    quote_symbol = Fields.varchar()
