### 注册机制，所有模块注册的基础代码

default_group = 'default'

class Registry(object):
    """ Registry which support registering modules and group them by a keyname

    If group name is not provided, modules will be registered to default group.
    """

    def __init__(self, name:str):
        self._name = name
        self._modules = {default_group: {}}

    def __repr__(self) -> str:
        format_str = self.__class__.__name__ + f' ({self._name})\n'
        for group_name,group in self._modules.items():
            format_str += f'group_name={group_name}, modules={list(group.keys())}\n'

        return format_str

    @property
    def name(self) -> str:
        return self._name

    @property
    def modules(self) -> dict:
        return self._modules

    def get(self, module_key, group_key=default_group):
        """ get module by key

        Args:
            module_key: module key
            group_key: group key
        """
        if module_key not in self._modules:
            return None
        else:
            return self._modules[group_key].get(module_key, None)

    def _register_module(self,
                         group_key=default_group,
                         module_name=None,
                         module_cls=None,
                         force=False):
        assert isinstance(group_key,
                          str), 'group_key is required and must be str'

        if group_key not in self._modules:
            self._modules[group_key] = {}

        # Some registered module_cls can be function type.
        # if not inspect.isclass(module_cls):
        #     raise ValueError('module_cls is required and must be a class')

        if module_name is None:
            module_name = module_cls.__name__

        if module_name in self._modules[group_key] and not force:
            raise KeyError(f'{module_name} is already registered in '
                           f'{self._name}[{group_key}]')
        self._modules[group_key][module_name] = module_cls
        module_cls.group_key = group_key

    def register_module(self,
                        group_key: str = default_group,
                        module_name: str = None,
                        module_cls: str = None,
                        force=False):
        """ register module

        Example:
            >>> models = Registry('models')
            >>> @models.register_module('image-classification', 'SwinT')
            >>> class SwinTransformer:
            >>>     pass

            >>> @models.register_module('SwinDefault')
            >>> class SwinTransformerDefaultGroup:
            >>>     pass

            >>> class SwinTransformer2:
            >>>     pass
            >>> MODELS.register_module('image-classification',
                                        module_name='SwinT2',
                                        module_cls=SwinTransformer2)

        Args:
            group_key: Group name of which module will be registered,
                default group name is 'default'
            module_name: Module name
            module_cls: Module class object
            force (bool, optional): Whether to override an existing class with
                the same name. Default: False.
        """
        if not (module_name is None or isinstance(module_name, str)):
            raise TypeError(f'module_name must be either of None, str,'
                            f'got {type(module_name)}')
        if module_cls is not None:
            self._register_module(
                group_key=group_key,
                module_name=module_name,
                module_cls=module_cls,
                force=force)
            return module_cls

        # if module_cls is None, should return a decorator function
        def _register(module_cls):
            self._register_module(
                group_key=group_key,
                module_name=module_name,
                module_cls=module_cls,
                force=force)
            return module_cls

        return _register

# Todo: 通过配置文件注册对应模块，还未确定config的组织形式
def build_from_cfg(cfg,
                   registry: Registry,
                   group_key: str = default_group,
                   default_args: dict = None) -> object:
    """Build a module from config dict when it is a class configuration, or
    call a function from config dict when it is a function configuration.

    Example:
        >>> models = Registry('models')
        >>> @models.register_module('image-classification', 'SwinT')
        >>> class SwinTransformer:
        >>>     pass
        >>> swint = build_from_cfg(dict(type='SwinT'), MODELS,
        >>>     'image-classification')
        >>> # Returns an instantiated object
        >>>
        >>> @MODELS.register_module()
        >>> def swin_transformer():
        >>>     pass
        >>>       = build_from_cfg(dict(type='swin_transformer'), MODELS)
        >>> # Return a result of the calling function

    Args:
        cfg (dict): Config dict. It should at least contain the key "type".
        registry (:obj:`Registry`): The registry to search the type from.
        group_key (str, optional): The name of registry group from which
            module should be searched.
        default_args (dict, optional): Default initialization arguments.
        type_name (str, optional): The name of the type in the config.
    Returns:
        object: The constructed object.
    """
    pass