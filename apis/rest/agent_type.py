from flask import jsonify
from flask_restful import Resource
from processing import agent_type
from processing.user_role import authorized_groups

class AgentTypeEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, agent_type_id='all'):
        return jsonify(agent_type.get_agent_type(agent_type_id))

