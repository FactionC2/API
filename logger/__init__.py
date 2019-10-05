from datetime import datetime
import logging
from os import environ

default_level = logging.INFO

def log(source, message, level="info"):
    msg = f"[{str(source)}] - {str(message)}"

    if int(environ.get("USE_NATIVE_LOGGER", 0)) == 1:
        if not isinstance(level, int):
            level = getattr(logging, level.upper(), default_level)
        logger = logging.getLogger()
        logger.log(level, msg)

    else:
        print("({0}){1}".format(datetime.now().strftime("%m/%d %H:%M:%S"), msg))

