import logging
import sys
from datetime import datetime
from nseapi.generic import validate_directory
import nseapi.constant as c


def get_logger(name):
    # Create a custom logger
    logger = logging.getLogger(name)

    now = datetime.now()
    now_str = now.strftime("%d-%m-%Y")

    # Create handlers
    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler(stream=sys.stdout)
    dir_path = c.HOME_DIR_PATH.joinpath('log')
    validate_directory(dir_path)
    file_path = dir_path.joinpath(name + '_' + now_str + '.log')
    f_handler = logging.FileHandler(file_path)
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%d-%m-%y %I:%M:%S %p")
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%d-%m-%y %I:%M:%S %p")
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
