from app.db import DatabaseClient
from .utils import list_to_str

def update_balances(balances):
    if balances == []:
        return

    client = DatabaseClient()

    amount_case = []
    price_case = []
    balance_ids = []
    for balance in balances:
        amount_case.append(f"WHEN id = {balance['balance_id']} THEN {balance['partial_amount']}")
        price_case.append(f"WHEN id = {balance['balance_id']} THEN {balance['partial_price']}")
        balance_ids.append(balance['balance_id'])

    sql_query = f"""
UPDATE balances
SET amount = amount + (CASE {list_to_str(amount_case)} END),
    price = price + (CASE {list_to_str(price_case)} END)
WHERE id IN ({list_to_str(balance_ids)});
    """

    client.manual(sql_query, False)
    client.disconect()
