from orm import Fields, Model

class Holding(Model):
    _table = 'holding'

    id = Fields.id()
    user_id = Fields.reference()
    amount = Fields.double()
    base_symbol = Fields.varchar()
    # TODO: Remove price and quote_symbol
    price = Fields.double()
    quote_symbol = Fields.varchar()
