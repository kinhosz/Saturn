from . import handshake

def execute(cursor, sql_insert):
    try:
        cursor.execute(sql_insert)
    except Exception as e:
        print("Error when executing this query:", sql_insert, "Exception:", e)
        return None
    
    response = cursor.fetchall()

    return response

def insert(cursor, table, columns, values):
    sql_insert = "INSERT INTO " + str(table)
    sql_insert = sql_insert + "(" + ", ".join(columns) + ") "
    sql_insert = sql_insert + "VALUES(" + ", ".join(handshake.convertEachToStr(values)) + ") "
    sql_insert = sql_insert + "RETURNING " + "id"

    return execute(cursor, sql_insert)
