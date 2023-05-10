import pydoc
import sys
from importlib import import_module
from pathlib import Path
from typing import Union
from addict import Dict


class ConfigDict(Dict):
    """
__missing__方法在字典中找不到指定的键时被调用。在这个实现中，它会抛出一个KeyError异常，其中包含未找到的键的名称。
__getattr__方法在尝试访问不存在的属性时被调用。它首先尝试调用父类（super()）的__getattr__方法来获取属性值。如果父类的__getattr__方法引发了KeyError异常，那么它会创建一个AttributeError异常，并提供相应的错误消息，指示属性不存在。

这个类的作用是创建一个字典对象，在访问不存在的键或属性时，抛出类似于标准字典和对象的异常，以提供更好的错误信息。
    """
    def __missing__(self, name):
        raise KeyError(name)

    def __getattr__(self, name):
        try:
            value = super().__getattr__(name)
        except KeyError:
            ex = AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        else:
            return value
        raise ex


def py2dict(file_path: Union[str, Path]) -> dict:
    """Convert python file to dictionary.
    The main use - config parser.
    file:
    ```
    a = 1
    b = 3
    c = range(10)
    ```
    will be converted to
    {'a':1,
     'b':3,
     'c': range(10)
    }
    Args:
        file_path: path to the original python file.
    Returns: {key: value}, where key - all variables defined in the file and value is their value.
    """
    file_path = Path(file_path).absolute()

    if file_path.suffix != ".py":
        raise TypeError(f"Only Py file can be parsed, but got {file_path.name} instead.")

    if not file_path.exists():
        raise FileExistsError(f"There is no file at the path {file_path}")

    module_name = file_path.stem

    if "." in module_name:
        raise ValueError("Dots are not allowed in config file path.")

    config_dir = str(file_path.parent)

    sys.path.insert(0, config_dir)

    mod = import_module(module_name)
    sys.path.pop(0)
    cfg_dict = {name: value for name, value in mod.__dict__.items() if not name.startswith("__")}

    return cfg_dict


def py2cfg(file_path: Union[str, Path]) -> ConfigDict:
    cfg_dict = py2dict(file_path)

    return ConfigDict(cfg_dict)


def object_from_dict(d, parent=None, **default_kwargs):
    """
    该函数接受一个字典d作为参数，以及可选的parent对象和其他关键字参数default_kwargs。

    函数首先复制字典d，并将其存储在变量kwargs中。然后，它从kwargs中弹出键为"type"的值，并将其存储在变量object_type中。
    接下来，函数遍历default_kwargs中的每个键值对，将其添加到kwargs中，如果键在kwargs中不存在的话。

    如果parent参数不为None，则函数返回parent对象的属性object_type所对应的方法，并以kwargs作为关键字参数进行调用。
    这样做的目的是创建一个属于parent对象的子对象。

    如果parent参数为None，则函数使用pydoc.locate函数根据object_type的值查找对应的对象类型，
    并以kwargs作为关键字参数进行实例化。这种方式用于在全局范围内创建对象。

    该函数的目的是根据提供的字典创建一个对象。
    字典中的键值对应于对象的属性和对应的值。
    通过传入parent参数，可以创建属于某个父对象的子对象。
    同时，通过default_kwargs参数，可以提供默认的属性值，在字典中不存在对应的键时使用这些默认值。
    :param d:
    :param parent:
    :param default_kwargs:
    :return:
    """
    kwargs = d.copy()
    object_type = kwargs.pop("type")
    for name, value in default_kwargs.items():
        kwargs.setdefault(name, value)

    if parent is not None:
        return getattr(parent, object_type)(**kwargs)  # skipcq PTC-W0034

    return pydoc.locate(object_type)(**kwargs)