from app.db import DatabaseClient

def activate_deposits(deposit_ids, btc_price):
    client = DatabaseClient()

    ids_in_str = ", ".join(map(str, deposit_ids))

    sql_query = f"""
        SELECT id, user_id, amount, stage
        FROM deposits
        WHERE id IN ({ids_in_str});
    """

    res = client.manual(sql_query)

    deposits_by_user = {}
    valid_deposits = []
    rejected_deposits = []
    for r in res:
        deposit_id, user_id, amount, stage = r
        if stage != 'PENDING':
            rejected_deposits.append(deposit_id)
            continue

        if user_id not in deposits_by_user.keys():
            deposits_by_user[user_id] = {
                'deposit_ids': [],
                'amount': 0.0
            }

        deposits_by_user[user_id]['deposit_ids'].append(deposit_id)
        deposits_by_user[user_id]['amount'] += amount
        valid_deposits.append(deposit_id)

    print("{} deposits were rejecteds".format(rejected_deposits))

    ids_in_str = ", ".join(map(str, valid_deposits))

    sql_query = f"""
        UPDATE deposits
        SET stage = 'CONFIRMED'
        WHERE id IN ({ids_in_str});
    """

    client.manual(sql_query, False)

    sql_query = f"""
        SELECT id, user_id, amount, price
        FROM balances
        WHERE user_id IN ({ids_in_str})
        AND base_symbol = 'BRL';
    """

    res = client.manual(sql_query)

    balances = []
    for r in res:
        balance_id, user_id, amount, price = r

        new_amount = amount + deposits_by_user[user_id]['amount']
        new_price = price + (deposits_by_user[user_id]['amount'] / btc_price)
        balances.append((balance_id, new_amount, new_price))

    case_amount = ""
    case_price = ""

    balance_ids = []

    for balance in balances:
        case_amount += f"WHEN id = {balance[0]} THEN {balance[1]}\n"
        case_price += f"WHEN id = {balance[0]} THEN {balance[2]}\n"
        balance_ids.append(balance[0])

    balance_ids_str = ", ".join(map(str, balance_ids))

    sql_query = f"""
        UPDATE balances
        SET
            amount = CASE
                {case_amount}
            END,
            price = CASE
                {case_price}
            END
        WHERE id IN ({balance_ids_str});
    """

    client.manual(sql_query, False)
    client.disconect()
    print("OK")
