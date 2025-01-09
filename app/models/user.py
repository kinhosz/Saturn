from orm import Fields, Model

class User(Model):
    _table = 'users'

    id = Fields.id()
    telegram_chat_id = Fields.integer()
    telegram_username = Fields.varchar()
    active = Fields.boolean()
