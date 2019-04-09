from flask import jsonify, request, send_file
from flask_restful import Resource, reqparse
from processing import payload
from processing.user_role import authorized_groups

payload_parser = reqparse.RequestParser()
payload_parser.add_argument('Description')
payload_parser.add_argument('AgentType')
payload_parser.add_argument('AgentTypeFormat')
payload_parser.add_argument('TransportId', type=int)
payload_parser.add_argument('Architecture')
payload_parser.add_argument('Version')
payload_parser.add_argument('Format')
payload_parser.add_argument('AgentTypeConfiguration')
payload_parser.add_argument('Jitter', type=float)
payload_parser.add_argument('BeaconInterval', type=int)
payload_parser.add_argument('ExpirationDate')
payload_parser.add_argument('Enabled', type=bool)
payload_parser.add_argument('Visible', type=bool)

class PayloadEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, payload_id='all'):
        return jsonify(payload.get_payload(payload_id))

    @authorized_groups(['StandardWrite'])
    def post(self):
        args = payload_parser.parse_args()
        return jsonify(payload.new_payload(description=args['Description'],
                                           agent_type=args['AgentType'],
                                           agent_type_format=args['AgentTypeFormat'],
                                           agent_transport_id=args['AgentTransportId'],
                                           transport_id=args['TransportId'],
                                           operating_system=args['OperatingSystem'],
                                           architecture=args['Architecture'],
                                           version=args['Version'],
                                           format=args['Format'],
                                           agent_type_configuration=args['AgentTypeConfiguration'],
                                           jitter=args['Jitter'],
                                           interval=args['BeaconInterval'],
                                           expiration_date=args['ExpirationDate']))

    @authorized_groups(['StandardWrite'])
    def put(self, payload_id):
        args = payload_parser.parse_args()
        return jsonify(payload
                       .update_payload(
                            payload_id=payload_id,
                            jitter=args.get('Jitter'),
                            interval=args.get('BeaconInterval'),
                            expiration_date=args.get('ExpirationDate'),
                            enabled=args.get('Enabled'),
                            visible=args.get('Visible'))
                       )

    @authorized_groups(['StandardWrite'])
    def delete(self, payload_id):
        results = payload.update_payload(payload_id, enabled=False, visible=False)
        if not results['Success']:
            response_code = 400
        else:
            response_code = 200
        return jsonify(results, response_code)


class PayloadFileEndpoint(Resource):
    def get(self, payload_id):
        result = payload.download_payload(payload_id)
        if result['Success']:
            print("[rest/payloadfile:get] sending {0}".format(result['Message']))
            return send_file(result['Message'], as_attachment=True, attachment_filename=result['Filename'])
        else:
            return jsonify({
                'Success': False,
                'Message': 'Could not download file'
            }, 400)

    def post(self, payload_id):
        build_token = request.headers.get('build-token')
        if build_token:
            result = payload.upload_payload(payload_id, build_token)
            if result['Success']:
                return jsonify(result)
        else:
            result = dict({
                'Success': False,
                'Message': "Upload failed."
            })
        return jsonify(result), 400