import logging as _logging
import sys, os
from datetime import datetime as _datetime
from typing import Union
from pathlib import Path as _Path
from nseapi.generic import validate_directory
import nseapi.constant as c


def get_logger(name: str, log_dir: Union[_Path, str]=None) -> _logging.Logger:
    """ Return Logger Object

    Args:
        name (str): name of logger
        log_dir (Union[_Path, str], optional): path of logger. Defaults to None.

    Returns:
        [logging.Logger]: logging.Logger
    """

    # Create a custom logger
    logger = _logging.getLogger(name)

    now = _datetime.now()
    now_str = now.strftime("%d-%m-%Y")

    # Create handlers
    logger.setLevel(_logging.DEBUG)

    # Command line logger
    c_handler = _logging.StreamHandler(stream=sys.stdout)
    c_handler.setLevel(_logging.DEBUG)
    c_format = _logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%d-%m-%y %I:%M:%S %p")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File Handler
    if log_dir is not None:
        if isinstance(log_dir, str):
            log_dir = _Path(log_dir)

        if validate_directory(log_dir):
            file_name = log_dir.joinpath(name + '_' + now_str + '.log')
            f_handler = _logging.FileHandler(file_name)
            f_handler.setLevel(_logging.INFO)
            f_format = _logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%d-%m-%y %I:%M:%S %p")
            f_handler.setFormatter(f_format)
            logger.addHandler(f_handler)

    return logger

