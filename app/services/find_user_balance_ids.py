from app.db import DatabaseClient
from .utils import list_to_str

def find_user_balance_ids(user_ids):
    client = DatabaseClient()

    sql_query = f"""
SELECT id, user_id
FROM balances
WHERE user_id IN ({list_to_str(user_ids)});
    """
    res = client.manual(sql_query)
    client.disconect()

    balances_by_user_id = {}
    for r in res:
        balances_by_user_id[r[1]] = r[0]

    return balances_by_user_id
    