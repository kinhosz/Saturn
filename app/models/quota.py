from orm import Fields, Model

class Quota(Model):
    _table = 'quotas'

    id = Fields.id()
    user_id = Fields.reference()
    quota_state = Fields.varchar()
    amount = Fields.double()
    price = Fields.double()
    created_at = Fields.timestamp()
