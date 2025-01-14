from orm import Fields, Model

class Deposit(Model):
    _table = 'deposits'

    id = Fields.id()
    user_id = Fields.reference()
    amount = Fields.double()
    stage = Fields.varchar()
