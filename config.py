import os
import json
from logger import log


config_file_path = '/opt/faction/global/config.json'

def get_config():
    try:
        if os.path.exists(config_file_path):
            with open(config_file_path) as f:
                config = json.load(f)
            return config
        else:
            config = dict()
            config["API_UPLOAD_DIR"] = os.environ["API_UPLOAD_DIR"]
            config["FLASK_SECRET"] = os.environ["FLASK_SECRET"]
            config["POSTGRES_DATABASE"] = os.environ["POSTGRES_DATABASE"]
            config["POSTGRES_USERNAME"] = os.environ["POSTGRES_USERNAME"]
            config["POSTGRES_PASSWORD"] = os.environ["POSTGRES_PASSWORD"]
            config["POSTGRES_HOST"] = os.environ["POSTGRES_HOST"]
            config["RABBIT_USERNAME"] = os.environ["RABBIT_USERNAME"]
            config["RABBIT_PASSWORD"] = os.environ["RABBIT_PASSWORD"]
            config["RABBIT_HOST"] = os.environ["RABBIT_HOST"]
            return config
    except:
        log("config.py", "Could not load config file: {0}".format(config_file_path))
        exit(1)

FACTION_CONFIG = get_config()

SECRET_KEY = FACTION_CONFIG["FLASK_SECRET"]
#SALT = '<THIS SHOULD ALSO BE CHANGED>'
#ADMIN_USERNAME = 'admin'
#ADMIN_PASSWORD = 'FactionRocksSocks' # Faction does indeed rock socks, but you change this
RABBIT_HOST = FACTION_CONFIG["RABBIT_HOST"]
RABBIT_USERNAME = FACTION_CONFIG["RABBIT_USERNAME"]
RABBIT_PASSWORD = FACTION_CONFIG["RABBIT_PASSWORD"]
RABBIT_URL = 'amqp://{}:{}@{}:5672/%2F'.format(RABBIT_USERNAME, RABBIT_PASSWORD, RABBIT_HOST)
#RABBIT_HOST = '192.168.1.49'
DB_USER = FACTION_CONFIG["POSTGRES_USERNAME"]
DB_PASSWORD = FACTION_CONFIG["POSTGRES_PASSWORD"]
DB_HOST = FACTION_CONFIG["POSTGRES_HOST"]
DB_NAME = FACTION_CONFIG["POSTGRES_DATABASE"]
DB_URI = 'postgresql://{}:{}@{}/{}?client_encoding=utf8'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
UPLOAD_DIR = FACTION_CONFIG["API_UPLOAD_DIR"]