from app.db import handshake

def execute(sql_query):
    conn = handshake.connect()
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
    except Exception as e:
        print("Error when executing this query:", sql_query, "Exception:", e)
        return None
    
    response = cursor.fetchall()
    handshake.disconnect(conn)

    return response

def find_equal(table, column, equal_to, view = ['*']):
    sql_query = 'SELECT ' + ', '.join(handshake.convertEachToStr(view))
    sql_query = sql_query + ' FROM ' + str(table)
    sql_query = sql_query + ' WHERE ' + str(column) + ' = '

    if str(equal_to).isnumeric():
        sql_query = sql_query + str(equal_to)
    else:
        sql_query = sql_query + "\'" + str(equal_to) + "\'"

    return execute(sql_query)

def less_than(table, column, less_than, view = ['*']):
    sql_query = 'SELECT ' + ', '.join(handshake.convertEachToStr(view))
    sql_query = sql_query + ' FROM ' + str(table)
    sql_query = sql_query + ' WHERE ' + str(column) + ' = ' + str(less_than)

    return execute(sql_query)

def manual(sql_query):
    return execute(sql_query)

