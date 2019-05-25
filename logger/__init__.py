from datetime import datetime


def log(source, message):
    print("({0})[{1}] - {2}".format(datetime.now().strftime("%m/%d %H:%M:%S"), source, message))

