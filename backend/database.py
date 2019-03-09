from time import sleep
import psycopg2
from flask_sqlalchemy import SQLAlchemy

from config import DB_URI

db_connected = False
print("[database.py] Checking Database..")
while not db_connected:
    try:
        db_connection = psycopg2.connect(DB_URI, connect_timeout=5)
        db_connection.cursor()
        db_connected = True
        print("[database.py] Database is up!")
        db_connection.close()
    except Exception as e:
        print("[database.py] Database not reachable, will wait. Error: {0}".format(str(e)))
        db_connected = False
        sleep(5)

db = SQLAlchemy()
