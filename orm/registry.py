import logging
logger = logging.getLogger(__name__)


class ModelRegistry:
    _models = {}

    @classmethod
    def register(cls, name, model_class):
        cls._models[name] = model_class

    @classmethod
    def get(cls, name):
        return cls._models[name]


class Env:
    def __getitem__(self, name):
        cls_model = ModelRegistry.get(name)
        if not cls_model:
            logger.error(f"Class '%s' does not exists in the registry", name)
        return cls_model
