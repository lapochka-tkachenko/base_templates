import logging
import os

import colorlog

from core.settings import BASE_DIR

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

_color_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    },
)

_file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(module)s | %(message)s')

_stream_handler = colorlog.StreamHandler()
_stream_handler.setLevel(logging.DEBUG)
_stream_handler.setFormatter(_color_formatter)

_file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'events.log'))
_file_handler.setLevel(logging.INFO)
_file_handler.setFormatter(_file_formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(_stream_handler)
root_logger.addHandler(_file_handler)

logger = logging.getLogger('event_logger')