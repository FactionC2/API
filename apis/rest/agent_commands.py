from flask import jsonify, request
from flask_restful import Resource, fields, reqparse
from processing import command
from processing.user_role import authorized_groups


class AgentCommandEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, agent_id):
        command_obj = command.get_commands_by_agent_id(agent_id)
        return jsonify(command_obj)
