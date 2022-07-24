import yaml
import logging

from dates_finder_logger import init_logger

def init_config_from_yaml(yaml_config_filename: str) -> dict:
    with open(yaml_config_filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

logger = init_logger()
logger.debug("Initializing config from yaml file")
GLOBAL_CONFIG = init_config_from_yaml('config.yaml')
logger.debug("Initialized the following config:")
logger.debug(GLOBAL_CONFIG)

if __name__ == '__main__':
    print(GLOBAL_CONFIG)