from .db import migrate

def db_config():
    print("===Configurating database===")
    migrate.main()
    print("===Finish database configuration===")

if __name__ == "__main__":
    db_config()
