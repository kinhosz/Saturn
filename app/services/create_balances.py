from app.db import DatabaseClient
from app.services.utils import list_to_str

def create_balances(user_ids):
    client = DatabaseClient()

    body = []
    for user_id in user_ids:
        body.append(f"({user_id}, 0.0, 'BRL', 0.0, 'BTC')")
        body.append(f"({user_id}, 0.0, 'BTC', 0.0, 'BRL')")

    sql_query = f"""
        INSERT INTO balances (user_id, amount, base_symbol, price, quote_symbol)
        VALUES
            {list_to_str(body)}
        ON CONFLICT (user_id, base_symbol, quote_symbol) DO NOTHING;
    """

    client.manual(sql_query, False)
    client.disconect()

    print("Balances Created for users: {}".format(user_ids))
