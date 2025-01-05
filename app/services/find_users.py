from app.db import DatabaseClient
from .utils import list_to_str

def find_users(ids):
    if ids == []:
        return []

    client = DatabaseClient()

    sql_query = f"""
SELECT id, telegram_chat_id, telegram_username, active
FROM users
WHERE id IN ({list_to_str(ids)});
    """

    res = client.manual(sql_query)
    client.disconect()

    users = []
    for r in res:
        users.append({
            'id': r[0],
            'telegram_chat_id': r[1],
            'telegram_username': r[2],
            'active': r[3]
        })

    return users
