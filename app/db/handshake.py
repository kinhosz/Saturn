import psycopg2 as psy
import re
import os
from .setup import setup

def convertEachToStr(unsafe_list):
    safety = []
    for data in unsafe_list:
        if isinstance(data, str):
            v = "'{value}'".format(value=data)
        else:
            v = "{value}".format(value=data)
        safety.append(v)

    return safety

def getCredentials():
    cred = {
        'user': re.search('(?<=postgres://)\w+', os.getenv('DATABASE_URL')).group(0),
        'password': re.search('postgres://\w+:(\w+)', os.getenv('DATABASE_URL')).group(1),
        'host': re.search('postgres://\w+:\w+@([^:]*)', os.getenv('DATABASE_URL')).group(1),
        'port': re.search('postgres://\w+:\w+@[^:]*:(\w+)', os.getenv('DATABASE_URL')).group(1),
        'database': re.search('postgres://\w+:\w+@[^:]*:\w+/(\w+)', os.getenv('DATABASE_URL')).group(1)
    }
    return cred

def connect():
    db = getCredentials()
    setup(db)

    conn = None
    try:
        conn = psy.connect(
            host = db['host'],
            database = db['database'],
            user = db['user'],
            password = db['password'],
            port = db['port']
        )
        conn.autocommit = True

        cursor = conn.cursor()
        cursor.execute("SELECT version()")

        db_version = cursor.fetchone()

        cursor.close()
    except Exception as e:
        print("Error to connect database. Exception:", e)

    return conn

def disconnect(conn):
    conn.close()
