from datetime import datetime
import logging
from os import environ

DEFAULT_LEVEL_STR = environ.get("DEFAULT_LOGGING_LEVEL", "INFO")
DEFAULT_LEVEL = getattr(logging, DEFAULT_LEVEL_STR.upper(), "INFO")
ROOT_LOGGER = logging.getLogger() # get root logger

if environ.get("GUNICORN_SERVER", "gunicorn") == "flask":
    ROOT_LOGGER.setLevel(DEFAULT_LEVEL) # set default level if using the flask server

def log(source, message, level="info"):
    msg = f"[{str(source)}] - {str(message)}"

    if int(environ.get("USE_NATIVE_LOGGER", 0)) == 1:
        if not isinstance(level, int):
            level = getattr(logging, level.upper(), DEFAULT_LEVEL)
        logger = logging.getLogger() # get root logger
        if len(logger.handlers) < 1: # if no handlers are passed in, setup default console handler
            ch = logging.StreamHandler()
            ch.setLevel(DEFAULT_LEVEL)
            logger.addHandler(ch)
            logger.log(DEFAULT_LEVEL, "[logger] - Setting Up Default Handler at level 'INFO' Becase No Handlers Were Found")
        logger.log(level, msg)

    else:
        print("({0}){1}".format(datetime.now().strftime("%m/%d %H:%M:%S"), msg))

