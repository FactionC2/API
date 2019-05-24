from flask import jsonify, request, send_file
from flask_restful import Resource, reqparse
from processing import faction_file
from processing.user_role import authorized_groups
from logger import log

faction_file_parser = reqparse.RequestParser()
faction_file_parser.add_argument('Hash')
faction_file_parser.add_argument('AgentName')
faction_file_parser.add_argument('FileName')
faction_file_parser.add_argument('FileContent')
faction_file_parser.add_argument('Visible')


class FactionFileEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, faction_file_name):
        result = faction_file.get_faction_file(faction_file_name)
        if result['Success']:
            return jsonify(result)
        return jsonify({
            'Success': False,
            'Message': 'Could not download file'
        }, 400)

    @authorized_groups(['StandardWrite', 'FileUpload'])
    def post(self):
        args = faction_file_parser.parse_args()
        log("FactionFileEndpoint:post", "got args: {0}".format(args))
        result = faction_file.upload_faction_file(args["AgentName"], args["Hash"], args["FileName"], args["FileContent"])
        if result['Success']:
            return jsonify(result)
        else:
            return jsonify(result), 400


class FactionFileDownloadEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, faction_file_name):
        result = faction_file.download_faction_file(faction_file_name)
        if result['Success']:
            log("rest/faction_file:get", "sending {0}".format(result['Message']))
            return send_file(result['Message'], as_attachment=True, attachment_filename=result['Filename'])
        return jsonify({
            'Success': False,
            'Message': 'Could not download file'
        }, 400)


class FactionFileBytesEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, faction_file_name):
        result = faction_file.get_faction_file_bytes(faction_file_name)
        if result['Success']:
            return jsonify(result)
        else:
            return jsonify({
                'Success': False,
                'Message': 'Could not get file bytes'
            }, 400)