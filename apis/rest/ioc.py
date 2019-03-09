from flask import jsonify
from flask_restful import Resource
from processing import ioc


class IOCEndpoint(Resource):
    def get(self, ioc_id='all'):
        print('[IOCEndpoint:GET] IOC Id: %s' % (ioc_id))
        iocs = ioc.get_ioc(ioc_id)
        return jsonify(iocs)