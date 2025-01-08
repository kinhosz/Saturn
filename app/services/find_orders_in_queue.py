from app.db import DatabaseClient
from .utils import list_to_str

def find_orders_in_queue():
    client = DatabaseClient()

    columns = [
        'id', 'user_id', 'foxbit_order_id', 'client_order_id', 'market_symbol',
        'side', 'market_type', 'order_state', 'price', 'price_avg', 'quantity', 'quantity_executed',
        'instant_amount', 'instant_amount_executed', 'created_at', 'trades_count', 'remark',
        'funds_received', 'fee_paid', 'post_only', 'time_in_force', 'cancellation_reason'
    ]

    sql_query = f"""
SELECT
    {list_to_str(columns)}
FROM orders
WHERE order_state IN ('ACTIVE', 'PARTIALLY_FILLED');
    """
    res = client.manual(sql_query)
    client.disconect()

    orders = {}
    for r in res:
        mapped_order = {}
        for i in range(len(columns)):
            mapped_order[columns[i]] = r[i]
        orders[mapped_order['id']] = mapped_order

    return orders
    