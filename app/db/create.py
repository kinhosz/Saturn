import psycopg2 as psy
import re
import os
from db import handshake

def execute(filename, cursor):
    path = './app/db/statements/' + filename + '.sql'
    f = open(path)
    command = (f.read())
    f.close()

    cursor.execute('SELECT version()')
    print(cursor.fetchone())

    try:
        cursor.execute(command)
    except:
        print("erro")

    cursor.close()

def commands(cursor):
    execute('create_table', cursor)

def main():
    conn = handshake.connect()
    commands(conn.cursor())
    handshake.disconnect(conn)

if __name__ == "__main__":
    main()