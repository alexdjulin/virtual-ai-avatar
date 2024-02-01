import os
import logging
from config_loader import config

NAMESPACE = 'AiAvatar'

# CREATE ROOT LOGGER
try:
    levels = {'NOTSET': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
    log_level = levels[config['log_level'].upper()]
    log_format = config['log_format']
    log_file = config['log_file'].replace('<avatar_name>', config['avatar_name'])
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(level=log_level, format=log_format, filename=log_file)

except Exception as error:
    # create default logger
    log_level = 20  # INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_file = 'logs/avatar.log'
    logging.basicConfig(level=log_level, format=log_format, filename=log_file)

logging.getLogger(NAMESPACE)


def get_logger(name: str) -> logging.Logger:
    ''' Creates child logger inside namespace '''
    return logging.getLogger(f'{NAMESPACE}.{name}')
