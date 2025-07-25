from .meta import MetaModel
from .registry import Env
from .fields import Fields
from .queries import _select_by, _insert, _update, _where

from datetime import datetime

class Model(metaclass=MetaModel):
    _connection = None
    env = Env()

    def __init_subclass__(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, Fields.Field):
                attr_value.name = attr_name

    def __init__(self, id=False):
        self._data = { 'id': id }

    def save(self):
        values_to_save = {}
        for k, v in self._data.items():
            if k == 'id' or v == None:
                continue
            if isinstance(v, datetime):
               values_to_save[k] = f"'{v.isoformat(sep=' ', timespec='milliseconds')}'"
            elif isinstance(v, str):
                values_to_save[k] = f"'{v}'"
            else:
                values_to_save[k] = v

        if values_to_save == {}:
            return

        sql = None
        if not self._data['id']:
            sql = _insert(self._table, values_to_save)
            id = self._transaction(sql, True)
            self._data['id'] = id
        else:
            sql = _update(self._table, self._data['id'], values_to_save)
            self._transaction(sql)

    ''' ClassMethods '''

    @classmethod
    def set_connection(cls, conn):
        cls._connection = conn

    @classmethod
    def _transaction(cls, sql, insert=False):
        id = False
        cursor = cls._connection.cursor()
        try:
            cursor.execute("BEGIN;")
            cursor.execute(sql)
            if insert:
                id = cursor.fetchone()[0]
            cursor.execute("COMMIT;")
        except Exception as e:
            print(f"_transaction error {e}")
            cls._connection.rollback()
        cursor.close()

        return id

    @classmethod
    def _fetch(cls, sql):
        cursor = cls._connection.cursor()
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()

        return res

    @classmethod
    def _single_fetch(cls, sql):
        res = cls._fetch(sql)

        if res == []:
            return None
        return res[0]

    @classmethod
    def find_by(cls, k, v):
        sql = _select_by(cls._table, k, v)
        res = cls._single_fetch(sql)
        if not res:
            return None

        return cls(res[0])

    @classmethod
    def where(cls, **kwargs):
        ''' The values for each kwarg should be a list '''
        sql = _where(cls._table, **kwargs)
        res = cls._fetch(sql)
        records = []
        for r in res:
            records.append(cls(r[0]))
        return records

    @classmethod
    def manual(cls, sql, fetch=True):
        cursor = cls._connection.cursor()

        try:
            cursor.execute(sql)
        except Exception as e:
            print("Error when executing this query:", sql, "Exception:", e)
            cursor.close()
            return None

        if not fetch:
            return None

        response = cursor.fetchall()
        cursor.close()
        return response
