from datetime import datetime
import os

"""
CONFIGURABLES
"""
LOG_PATH = 'logs'


def get_log_path(identifier=None) -> str:
    now = datetime.now()
    path = LOG_PATH + '/' + now.strftime('%Y/%m/%d')
    os.makedirs(path, exist_ok=True)
    if identifier:
        filename = '{}_{}.txt'.format(identifier, now.strftime('%H%M%S'))
        return '{}/{}'.format(path, filename)
    return path
