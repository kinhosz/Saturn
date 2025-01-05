from app.db import DatabaseClient
from app.foxbit.constants import *
from .utils import list_to_str

def write_orders(orders):
    if orders == []:
        return

    client = DatabaseClient()

    columns = [
        'user_id', 'foxbit_order_id', 'client_order_id', 'market_symbol',
        'side', 'market_type', 'order_state', 'price', 'quantity', 'quantity_executed',
    ]

    str_column = [
        'foxbit_order_id', 'client_order_id', 'market_symbol', 'side', 'market_type', 'order_state'
    ]

    values = []

    for order in orders:
        to_insert = []
        for c in columns:
            if not order.get(c, False):
                to_insert.append('NULL')
            elif c in str_column:
                to_insert.append(f"'{order[c]}'")
            else:
                to_insert.append(order[c])

        values.append(f"({list_to_str(to_insert)})")

    sql_query = f"""
INSERT INTO orders ({list_to_str(columns)})
VALUES {list_to_str(values)};
    """

    client.manual(sql_query, False)
    client.disconect()
