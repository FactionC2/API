from flask import jsonify
from flask_restful import Resource, reqparse
from processing.user_role import authorized_groups
from processing.transport import get_transport, new_transport, update_transport


# These parsers take arguments from a rest request and parse them
transport_parser = reqparse.RequestParser()
transport_parser.add_argument('Name')
transport_parser.add_argument('TransportType')
transport_parser.add_argument('Guid')
transport_parser.add_argument('Configuration')
transport_parser.add_argument('Enabled')
transport_parser.add_argument('Visible')


class TransportEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, transport_id='all'):
        log("transportEndpoint", "::get")
        response = get_transport(transport_id)
        return jsonify(response)

    @authorized_groups(['StandardWrite'])
    def post(self):
        args = transport_parser.parse_args()
        response = new_transport(transport_type=args['TransportType'])
        return jsonify(response)

    @authorized_groups(['StandardWrite', 'Transport'])
    def put(self, transport_id):
        args = transport_parser.parse_args()
        log("transportEndpoint", "::put got args: {0}".format(args))
        response = update_transport(transport_id=transport_id,
                                    name=args['Name'],
                                    transport_type=args['TransportType'],
                                    guid=args['Guid'],
                                    configuration=args['Configuration'],
                                    enabled=args['Enabled'],
                                    visible=args['Visible'])
        return jsonify(response)

    @authorized_groups(['StandardWrite', 'Transport'])
    def delete(self, transport_id):
        args = transport_parser.parse_args()
        log("transportEndpoint", "::put got args: {0}".format(args))
        response = update_transport(transport_id=transport_id,
                                    enabled=False,
                                    visible=False)
        return jsonify(response)