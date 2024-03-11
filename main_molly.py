from os import path

from lib.external.pythontools.config import get_settings_dict_from_yaml
from lib.internal.service.remote_node_monitor_service import run_molly, run_reset
from lib.internal.model.remote_node_monitor import RemoteNodeMonitorConfig


if __name__ == '__main__':
    run_molly(
        RemoteNodeMonitorConfig(
            get_settings_dict_from_yaml(
                path.join(path.dirname(path.abspath(__file__)), 'config', 'settings_config.yaml'),
                path.dirname(path.abspath(__file__))
            )
        )
    )
    
    
    # run_reset(
    #     RemoteNodeMonitorConfig(
    #         get_settings_dict_from_yaml(
    #             path.join(path.dirname(path.abspath(__file__)), 'config', 'settings_config.yaml'),
    #             path.dirname(path.abspath(__file__))
    #         )
    #     )
    # )
