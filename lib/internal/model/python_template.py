from lib.external.pythontools.dict_adaptable import DictAdaptable


# todo: insert application models
# end todo


# todo: remove these example models
class ExamplePrivateModelConfig(DictAdaptable):
    ExampleName: str
    ExampleAge: int


class PythonTemplateConfig(DictAdaptable):
    ExampleStr: str
    ExampleInt: int
    ExampleDict: dict
    ExampleFloat: float
    ExampleCustom: ExamplePrivateModelConfig
# end todo
