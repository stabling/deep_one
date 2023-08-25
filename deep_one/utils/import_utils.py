import os
from itertools import chain
from types import ModuleType

from deep_one.utils.logger import get_logger

logger = get_logger()


# 对模块进行懒加载
class LazyImportModule(ModuleType):
    """
    A module that is imported lazily.
    """
    def __init__(self,
                 name,
                 module_file,
                 import_structure,
                 module_spec=None,
                 extra_objects=None,
                 try_to_pre_import=False):
        super().__init__(name)
        self._modules = set(import_structure.keys())
        self._class_to_module = {}
        for key, values in import_structure.items():
            for value in values:
                self._class_to_module[value] = key
        # Needed for autocompletion in an IDE
        self.__all__ = list(import_structure.keys()) + list(
            chain(*import_structure.values()))
        self.__file__ = module_file
        self.__spec__ = module_spec
        self.__path__ = [os.path.dirname(module_file)]
        self._objects = {} if extra_objects is None else extra_objects
        self._name = name
        self._import_structure = import_structure
        if try_to_pre_import:
            self._try_to_import()

    def _try_to_import(self):
        for sub_module in self._class_to_module.keys():
            try:
                getattr(self, sub_module)
            except Exception as e:
                logger.warning(
                    f'pre load module {sub_module} error, please check {e}')

    # Needed for autocompletion in an IDE
    def __dir__(self):
        result = super().__dir__()
        # The elements of self.__all__ that are submodules may or may not be in the dir already, depending on whether
        # they have been accessed or not. So we only add the elements of self.__all__ that are not already in the dir.
        for attr in self.__all__:
            if attr not in result:
                result.append(attr)
        return result

    def __getattr__(self, name: str):
        if name in self._objects:
            return self._objects[name]
        if name in self._modules:
            value = self._get_module(name)
        elif name in self._class_to_module.keys():
            module = self._get_module(self._class_to_module[name])
            value = getattr(module, name)
        else:
            raise AttributeError(
                f'module {self.__name__} has no attribute {name}')

        setattr(self, name, value)
        return value