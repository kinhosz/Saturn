from . import handshake

def execute(sql_update):
    conn = handshake.connect()
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_update)
    except Exception as e:
        print("Error when executing this query:", sql_update, "Exception:", e)
        return None
    
    handshake.disconnect(conn)

def update(table, id, columns, values):
    sql_update = "UPDATE " + str(table) + " SET"
    
    data_size = len(columns)
    for i in range(data_size):
        column = str(columns[i])
        value = str(values[i])

        sql_update = sql_update + " " + column + " = " + value
        if i < data_size - 1:
            sql_update = sql_update + ","
    
    sql_update = sql_update + " WHERE id = " + str(id)

    execute(sql_update)
