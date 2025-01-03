from app.services import activate_users, activate_deposits
from app.db_config import db_config
from dotenv import load_dotenv

def run_activate_users():
    raw_input = str(input("Type the user ids: "))
    user_ids = [int(id) for id in raw_input.split()]

    activate_users(user_ids)

def run_activate_deposits():
    raw_input = str(input("Type the deposit ids: "))
    deposit_ids = [int(id) for id in raw_input.split()]
    btc_price = float(input("Type the Current Bitcoin Price: "))

    activate_deposits(deposit_ids, btc_price)

def main():
    menu_msg = "Choose your script:\n\n" \
            + "1) activate_users\n" \
            + "2) activate_deposits\n" \
            + "\n\n"

    method = int(input(menu_msg))

    if method == 1:
        run_activate_users()
    elif method == 2:
        run_activate_deposits()

if __name__ == "__main__":
    load_dotenv()
    db_config()
    main()
