from flask import jsonify
from flask_restful import Resource
from processing import ioc
from logger import log


class IOCEndpoint(Resource):
    def get(self, ioc_id='all'):
        log("IOCEndpoint:GET", "IOC Id:  {0}".format(ioc_id))
        iocs = ioc.get_ioc(ioc_id)
        return jsonify(iocs)