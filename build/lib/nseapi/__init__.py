from nseapi.requester import BaseApiAsync
import nseapi.constant as _c
from pathlib import Path as _Path
import os as _os
from datetime import datetime as _datetime

_c.HOME_DIR_PATH = _Path(__file__).parent
_c.TODAY_DATE = _datetime.now()

__all__ = ['BaseApiAsync']