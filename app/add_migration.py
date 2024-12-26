from datetime import datetime

MIGRATIONS_DIR = 'app/db/migrations/'

def main():
    description = input("Brief migration description: ")
    curr_timestamp = str(int(datetime.now().timestamp()))
    migration_filename = curr_timestamp + "_" + description.replace(" ", "_") + ".sql"

    sample = """BEGIN;

/*
    Add here your migration
*/

COMMIT;"""

    path = MIGRATIONS_DIR + migration_filename
    f = open(path, "w")
    f.write(sample)
    f.close()

    print("{migration} has been created.".format(migration=migration_filename))

if __name__ == "__main__":
    main()
