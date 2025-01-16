from app.services.utils import list_to_str
from orm import Model

def create_trading_settings(user_ids):
    body = []
    for user_id in user_ids:
        body.append(f"({user_id})")

    sql_query = f"""
        INSERT INTO trading_settings (user_id)
        VALUES
            {list_to_str(body)}
        ON CONFLICT (user_id) DO NOTHING;
    """

    print("Trading Settings Created for Users: {}".format(user_ids))

    Model.manual(sql_query, False)
