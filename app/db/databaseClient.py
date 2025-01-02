from . import handshake
from .insert import *
from .query import *
from .update import *

class DatabaseClient(object):
    def __init__(self):
        self._conn = handshake.connect()
        self._cursor = self._conn.cursor()

    def disconect(self):
        self._conn.close()

    def insert(self, table, columns, values):
        return insert(self._cursor, table, columns, values)

    def find_equal(self, table, column, value, view = ['*']):
        return find_equal(self._cursor, table, column, value, view)

    def less_than(self, table, column, value, view = ['*']):
        return less_than(self._cursor, table, column, value, view)

    def manual(self, sql_query, fetch=True):
        return manual(self._cursor, sql_query, fetch)

    def update(self, table, id, columns, values):
        return update(self._cursor, table, id, columns, values)
