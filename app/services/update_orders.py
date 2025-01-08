from app.db import DatabaseClient
from .utils import list_to_str

def update_orders(orders):
    if orders == {}:
        return

    client = DatabaseClient()

    columns = [
        'user_id', 'foxbit_order_id', 'client_order_id', 'market_symbol',
        'side', 'market_type', 'order_state', 'price', 'quantity', 'quantity_executed',
    ]
    str_column = [
        'foxbit_order_id', 'client_order_id', 'market_symbol', 'side', 'market_type', 'order_state'
    ]

    body = []
    for c in columns:
        case_str = ""
        for order in orders.values():
            val = f"'{order[c]}'" if c in str_column else order[c]
            when_str = f"WHEN id = {order['id']} THEN {val}\n"
            case_str += when_str
        body.append(f"{c} = (CASE {case_str} END)")

    sql_query = f"""
UPDATE orders
SET {list_to_str(body)}
WHERE id IN ({list_to_str(orders.keys())});
    """

    client.manual(sql_query, False)
    client.disconect()
