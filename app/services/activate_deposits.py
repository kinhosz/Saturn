from orm import Model

def activate_deposits(deposit_ids, btc_price):
    deposit_ids_in_str = ", ".join(map(str, deposit_ids))

    sql_query = f"""
        SELECT id, user_id, amount, stage
        FROM deposit
        WHERE id IN ({deposit_ids_in_str});
    """

    res = Model.manual(sql_query)

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

    valid_deposit_ids_in_str = ", ".join(map(str, valid_deposits))

    sql_query = f"""
        UPDATE deposit
        SET stage = 'CONFIRMED'
        WHERE id IN ({valid_deposit_ids_in_str});
    """

    Model.manual(sql_query, False)

    sql_query = f"""
        SELECT h.id, h.user_id, h.amount, h.price
        FROM holding AS h
        JOIN deposit AS d
        ON d.user_id = h.user_id
        WHERE d.id IN ({valid_deposit_ids_in_str})
        AND base_symbol = 'BRL';
    """

    res = Model.manual(sql_query)

    holdings = []
    for r in res:
        balance_id, user_id, amount, price = r

        new_amount = amount + deposits_by_user[user_id]['amount']
        new_price = price + (deposits_by_user[user_id]['amount'] / btc_price)
        holdings.append((balance_id, new_amount, new_price))

    case_amount = ""
    case_price = ""

    holding_ids = []

    for holding in holdings:
        case_amount += f"WHEN id = {holding[0]} THEN {holding[1]}\n"
        case_price += f"WHEN id = {holding[0]} THEN {holding[2]}\n"
        holding_ids.append(holding[0])

    holding_ids_str = ", ".join(map(str, holding_ids))

    sql_query = f"""
        UPDATE holding
        SET
            amount = CASE
                {case_amount}
            END,
            price = CASE
                {case_price}
            END
        WHERE id IN ({holding_ids_str});
    """

    Model.manual(sql_query, False)
    print("OK")
