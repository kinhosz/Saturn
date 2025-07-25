import logging
from .registry import ModelRegistry

logger = logging.getLogger(__name__)

class MetaModel(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        table = attrs.get('_table')
        if table:
            ModelRegistry.register(table, new_cls)
        elif name != 'Model':
            logger.warning(f"Class '%s' has not _table definition", name)

        return new_cls
