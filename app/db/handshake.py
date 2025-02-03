import psycopg2 as psy
import re
import os
from .setup import setup
from app.constant import env_name

def getCredentials():
    if env_name() == 'production':
        database_url = os.getenv('DATABASE_URL')
    elif env_name() == 'development':
        database_url = os.getenv('DATABASE_URL_DEV')
    else:
        database_url = os.getenv('DATABASE_URL_TEST')
        
    cred = {
        'user': re.search('(?<=postgres://)\w+', database_url).group(0),
        'password': re.search('postgres://\w+:(\w+)', database_url).group(1),
        'host': re.search('postgres://\w+:\w+@([^:]*)', database_url).group(1),
        'port': re.search('postgres://\w+:\w+@[^:]*:(\w+)', database_url).group(1),
        'database': re.search('postgres://\w+:\w+@[^:]*:\w+/(\w+)', database_url).group(1)
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
        conn.autocommit = env_name() != 'test'

        cursor = conn.cursor()
        cursor.execute("SELECT version()")

        db_version = cursor.fetchone()

        cursor.close()
    except Exception as e:
        print("Error to connect database. Exception:", e)

    return conn

def disconnect(conn):
    conn.close()
