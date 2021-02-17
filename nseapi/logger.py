import logging
import os
import sys
from datetime import datetime
from pathlib import Path


def get_logger(name):
    # Create a custom logger
    logger = logging.getLogger(name)

    now = datetime.now()
    now_str = now.strftime("%d-%m-%Y")

    # Create handlers
    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler(stream=sys.stdout)
    parent_path = Path(__file__).parent.parent
    file_name = parent_path.joinpath('log')
    file_name = file_name.joinpath(name + '_' + now_str + '.log')
    f_handler = logging.FileHandler(file_name)
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
