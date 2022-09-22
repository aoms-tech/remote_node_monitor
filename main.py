from os import path

from lib.external.pythontools.config import get_settings_dict_from_yaml
from lib.external.pythontools.setup_logging import make_logger, set_universal_logger

# todo: change to "from lib.internal.service.<application>_service import run_application"
from lib.internal.service.python_template_service import run_application
# end todo

# todo: change to "from lib.internal.model.<application> import <application_model>
from lib.internal.model.python_template import PythonTemplateConfig
# end todo


if __name__ == '__main__':
    # todo: make logger is called only if your application requires logging. Remove if not needed.
    make_logger(
        path.join(
            path.dirname(path.abspath(__file__)), 'config', 'settings_logging.yaml'),
        log_path='local'
    )
    # end todo

    # todo: Decide if you want all submodules to run off of the same logger. 'Demo' is the name of the logger and
    #   is defined in settings_logging.yaml
    set_universal_logger('demo')
    # end todo

    # todo: replace "PythonTemplateConfig" with your application's model
    run_application(
        PythonTemplateConfig(
            get_settings_dict_from_yaml(
                path.join(path.dirname(path.abspath(__file__)), 'config', 'settings_config.yaml'),
                path.dirname(path.abspath(__file__))
            )
        )
    )
    # end todo
