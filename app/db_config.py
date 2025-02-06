from .db import migrate

def db_config():
    print("===Configurating database===")
    conn = migrate.main()
    print("===Finish database configuration===")
    return conn

if __name__ == "__main__":
    db_config()
