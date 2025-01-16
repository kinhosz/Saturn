from .queries import _select
from datetime import datetime

class Fields:
    class Field:
        def __init__(self, field_type):
            self._field_type = field_type
            self._name = None

        def __set_name__(self, owner, name):
            self._name = name

        def __repr__(self):
            return f"<Field(name={self._name}, type={self._field_type})>"

        def __get__(self, record, owner):
            if self._name not in record._data.keys() and record._data['id']:
                sql = _select(record._table, record.id, self._name)
                value = owner._single_fetch(sql)
                if value:
                    value = value[0]
                record._data[self._name] = self._convert_from_database(value)

            return record._data.get(self._name, None)

        def __set__(self, record, value):
            if value:
                if self._field_type == 'boolean':
                    assert isinstance(value, bool), 'Expected to be a Bool'
                if self._field_type == 'double':
                    assert isinstance(value, float), 'Expected to be a float'
                if self._field_type in ('id', 'integer', 'reference'):
                    assert isinstance(value, int), 'Expeceted to be an int'
                if self._field_type == 'varchar':
                    assert isinstance(value, str), 'Expected to be a str'
                if self._field_type == 'timestamp':
                    assert isinstance(value, datetime), 'Expected to be a datetime'

            record._data[self._name] = value

        def _convert_from_database(self, value):
            if not value:
                return value

            if self._field_type == 'boolean':
                return bool(value)
            if self._field_type == 'double':
                return float(value)
            if self._field_type in ('id', 'integer', 'reference'):
                return int(value)
            if self._field_type == 'varchar':
                return str(value)
            if self._field_type == 'timestamp':
                if isinstance(value, datetime):
                    return value
                return datetime.fromisoformat(value)

    @staticmethod
    def boolean():
        return Fields.Field("boolean")

    @staticmethod
    def double():
        return Fields.Field("double")

    @staticmethod
    def id():
        return Fields.Field("id")

    @staticmethod
    def integer():
        return Fields.Field("integer")

    @staticmethod
    def reference():
        return Fields.Field("reference")

    @staticmethod
    def timestamp():
        return Fields.Field("timestamp")

    @staticmethod
    def varchar():
        return Fields.Field("varchar")
