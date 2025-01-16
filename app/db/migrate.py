from datetime import datetime
from pathlib import Path
from orm import Model
from . import handshake

MIGRATIONS_PATH = 'app/db/migrations'

def getCurrentMigration(cursor):
    command = """
SELECT last_migration_applied
FROM schema_migrations
WHERE id = 1;
    """

    cursor.execute(command)
    res = cursor.fetchone()

    return res[0]

def applyMigration(cursor, command):
    try:
        cursor.execute(command)
    except Exception as e:
        print("Exception: {error}".format(error=e))
        return False

    return True

def updateLastMigrationTimestamp(cursor, value):
    command = """
UPDATE schema_migrations
SET last_migration_applied = '{value}'
WHERE id = 1;
    """.format(value=value)

    try:
        cursor.execute(command)
    except Exception as e:
        print("Exception: {error}".format(error=e))

def pendingMigrations(cursor):
    folder = Path(MIGRATIONS_PATH)
    migrations = [f.name for f in folder.iterdir() if f.is_file()]
    migrations.sort()
    
    current_migration = getCurrentMigration(cursor)
    current_timestamp = int(current_migration.timestamp())

    pending_migrations = 0
    for migration in migrations:
        migration_ts = int(migration.split("_")[0])
        if current_timestamp >= migration_ts:
            continue
        pending_migrations += 1
        f = open(MIGRATIONS_PATH + "/" + migration)
        status = applyMigration(cursor, f.read())
        if not status:
            print("Migration {filename} has been failed. Aborting...".format(filename=migration))
            f.close()
            return None
        f.close()

    print("Ran {migrations_count} pending migrations.".format(migrations_count = pending_migrations))
    if pending_migrations == 0:
        return None

    last_migration_timestamp = int(migrations[-1].split("_")[0])
    last_migration_date = datetime.fromtimestamp(last_migration_timestamp).strftime("%Y-%m-%d %H:%M:%S")
    updateLastMigrationTimestamp(cursor, last_migration_date)

def main():
    conn = handshake.connect()
    Model.set_connection(conn)
    pendingMigrations(conn.cursor())

if __name__ == "__main__":
    main()
