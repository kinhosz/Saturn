from app.db import create

def db_config():
    print("===Configurate database===")
    create.main()
    print("===Finish database configuration===")

if __name__ == "__main__":
    db_config()