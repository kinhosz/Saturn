from app.services.utils import list_to_str
from app.services.create_balances import create_balances
from app.services.create_trading_settings import create_trading_settings
from orm import Model

def activate_users(user_ids):
    sql_query = f"""
        SELECT id, active
        FROM users
        WHERE id IN ({list_to_str(user_ids)});
    """

    res = Model.manual(sql_query)

    valid_ids = []
    for r in res:
        if not r[1]:
            valid_ids.append(r[0])

    print("{} ids were rejected".format(len(user_ids) - len(valid_ids)))

    if len(valid_ids) == 0:
        return None

    sql_query = f"""
        UPDATE users
        SET active = TRUE
        WHERE users.id IN ({list_to_str(valid_ids)});
    """

    print("Active Users: {}".format(valid_ids))

    Model.manual(sql_query, False)

    create_balances(valid_ids)
    create_trading_settings(valid_ids)
