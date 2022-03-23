from app.db import handshake

def execute(sql_insert):
    conn = handshake.connect()
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_insert)
    except Exception as e:
        print("Error when executing this query:", sql_insert, "Exception:", e)
    
    response = cursor.fetchall()
    handshake.disconnect(conn)

    return response

def insert(table, columns, values):
    sql_insert = "INSERT INTO " + table
    sql_insert = sql_insert + "(" + ", ".join(columns) + ") "
    sql_insert = sql_insert + "VALUES(" + ", ".join(values) + ") "
    sql_insert = sql_insert + "RETURNING " + "id"

    return execute(sql_insert)