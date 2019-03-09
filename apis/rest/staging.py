from flask import jsonify
from flask_restful import Resource, fields, reqparse
from processing.user_role import authorized_groups
from processing.staging import new_staging_message, get_staging_response


# These parsers take arguments from a rest request and parse them
staging_message_parser = reqparse.RequestParser()
staging_message_parser.add_argument('Message')


class StagingEndpoint(Resource):
    @authorized_groups(['StandardWrite', 'Transport'])
    def post(self, payload_name, staging_id):
        args = staging_message_parser.parse_args()
        response = new_staging_message(payload_name, staging_id, args['Message'])
        return jsonify(response)