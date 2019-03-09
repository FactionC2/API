from flask import jsonify, request, send_file
from flask_restful import Resource, reqparse
from processing.user_role import authorized_groups
from processing.error_message import new_error_message, get_error_message

error_message_parser = reqparse.RequestParser()
error_message_parser.add_argument('Name')
error_message_parser.add_argument('Message')


class ErrorMessageEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, error_message_id='all'):
        result = get_error_message(error_message_id)
        if result['Success']:
            return jsonify(result)
        return jsonify(result, 400)

    @authorized_groups(['StandardWrite'])
    def post(self):
        args = error_message_parser.parse_args()
        result = new_error_message(args["Name"], args["Message"])
        if result['Success']:
            return jsonify(result)
        return jsonify(result, 400)