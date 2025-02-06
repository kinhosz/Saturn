import psycopg2 as psy
from app.constant import env_name

DEFAULT_DATABASE = 'postgres'

def db_exist(cursor, database):
    if env_name == 'production':
        return True

    command = "SELECT datname FROM pg_database WHERE datname = '{database}';".format(database=database)
    cursor.execute(command)
    res = cursor.fetchone()
    if not res:
        return False

    return res[0] == database

def table_exist(cursor):
    command = f"""
SELECT EXISTS (
SELECT 1
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename = 'schema_migrations'
);
    """

    cursor.execute(command)
    res = cursor.fetchone()
    if not res:
        return False
    return res[0]

def create(cursor, database):
    command = "CREATE DATABASE {database};".format(database=database)
    cursor.execute(command)
    if db_exist(cursor, database):
        print("Created {database} database.".format(database=database))
    else:
        raise Exception("{database} database creation has been failed".format(database=database))

def drop(cursor, database):
    command = f"DROP DATABASE {database};"
    cursor.execute(command)

def configurate(credentials):
    conn = psy.connect(
        host = credentials['host'],
        database = credentials['database'],
        user = credentials['user'],
        password = credentials['password'],
        port = credentials['port']
    )
    conn.autocommit = True
    cursor = conn.cursor()

    if table_exist(cursor):
        cursor.close()
        return

    command = """
BEGIN;
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    last_migration_applied TIMESTAMP NOT NULL DEFAULT '1970-01-01 00:00:00 UTC'::timestamp
);
COMMIT;
    """
    cursor.execute(command)
    command = """
INSERT INTO schema_migrations DEFAULT VALUES;
    """
    cursor.execute(command)
    cursor.close()
    conn.close()

def setup(credentials):
    if env_name() != 'production':
        conn = psy.connect(
            host = credentials['host'],
            database = DEFAULT_DATABASE,
            user = credentials['user'],
            password = credentials['password'],
            port = credentials['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()

        if env_name() == 'test':
            if db_exist(cursor, credentials['database']):
                drop(cursor, credentials['database'])

        if not db_exist(cursor, credentials['database']):
            create(cursor, credentials['database'])
        cursor.close()

    configurate(credentials)
