import sys
sys.path.append("..")
from deep_one.utils.registry import Registry

register = Registry("models")

@register.register_module("image-classification", module_name="test")
class Test:
    def __init__(self) -> None:
        self.name = "test"


if __name__ == '__main__':
    test = Test()