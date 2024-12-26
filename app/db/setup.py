import psycopg2 as psy

DEFAULT_DATABASE = 'postgres'

def exist(cursor, database):
    command = "SELECT datname FROM pg_database WHERE datname = '{database}';".format(database=database)
    cursor.execute(command)
    res = cursor.fetchone()
    if not res:
        return False

    return res[0] == database

def create(cursor, database):
    command = "CREATE DATABASE {database};".format(database=database)
    cursor.execute(command)
    if exist(cursor, database):
        print("Created {database} database.".format(database=database))
    else:
        raise Exception("{database} database creation has been failed".format(database=database))

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

def setup(credentials):
    conn = psy.connect(
        host = credentials['host'],
        database = DEFAULT_DATABASE,
        user = credentials['user'],
        password = credentials['password'],
        port = credentials['port']
    )
    conn.autocommit = True
    cursor = conn.cursor()

    if not exist(cursor, credentials['database']):
        create(cursor, credentials['database'])
        cursor.close()
        configurate(credentials)
    else:
        cursor.close()
