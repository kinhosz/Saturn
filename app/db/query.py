from . import handshake

def execute(cursor, sql_query):
    try:
        cursor.execute(sql_query)
    except Exception as e:
        print("Error when executing this query:", sql_query, "Exception:", e)
        return None
    
    response = cursor.fetchall()

    return response

def find_equal(cursor, table, column, equal_to, view = ['*']):
    sql_query = 'SELECT ' + ', '.join(view)
    sql_query = sql_query + ' FROM ' + str(table)
    sql_query = sql_query + ' WHERE ' + str(column) + ' = '

    if str(equal_to).isnumeric():
        sql_query = sql_query + str(equal_to)
    else:
        sql_query = sql_query + "\'" + str(equal_to) + "\'"

    return execute(cursor, sql_query)

def less_than(cursor, table, column, less_than, view = ['*']):
    sql_query = 'SELECT ' + ', '.join(view)
    sql_query = sql_query + ' FROM ' + str(table)
    sql_query = sql_query + ' WHERE ' + str(column) + ' = ' + str(less_than)

    return execute(cursor, sql_query)

def manual(cursor, sql_query):
    return execute(cursor, sql_query)

