from app.services import activate_users
from app.db_config import db_config
from dotenv import load_dotenv

def run_activate_users():
    raw_input = str(input("Type the user ids: "))
    user_ids = [int(id) for id in raw_input.split()]

    activate_users(user_ids)

def main():
    menu_msg = "Choose your script:\n\n" \
            + "1) activate_users" \
            + "\n\n"

    method = int(input(menu_msg))

    if method == 1:
        run_activate_users()

if __name__ == "__main__":
    load_dotenv()
    db_config()
    main()
