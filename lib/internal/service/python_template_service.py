import logging

# todo: import models unique to this service
from lib.internal.model.python_template import PythonTemplateConfig, ExamplePrivateModelConfig
# end todo


# todo: import service functions from child services
# end todo


# todo: insert application functions
# end todo


# todo: remove these example functions
def log_name(config: ExamplePrivateModelConfig):
    logging.info(f"The name in ExamplePrivateModelConfig is: {config.ExampleName}")
    print("")


def add_int_to_float(config: PythonTemplateConfig):
    logging.info(f"ExampleFloat before: {config.ExampleFloat}")
    example_float_before = config.ExampleFloat
    config.ExampleFloat = config.ExampleFloat + float(config.ExampleInt)
    logging.info(f"The following math was done to ExampleFloat: {config.ExampleFloat} = {example_float_before}+{config.ExampleInt}")
    logging.info(f"ExampleFloat after: {config.ExampleFloat}")
    print("")


def print_dict_contents(config: PythonTemplateConfig):
    print("EXAMPLE DICTIONARY CONTENTS: ")
    for key in config.ExampleDict.keys():
        print(f"{key}: {config.ExampleDict[key]}")
    print("")
# end todo


# todo: change parameter to be the application's main model
# todo: write main application code here
def run_application(config: PythonTemplateConfig):
    logging.info("Welcome to the python template application.")
    print("")
    add_int_to_float(config)
    print_dict_contents(config)
    log_name(config.ExampleCustom)
# end todo
