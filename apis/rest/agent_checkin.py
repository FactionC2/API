from flask import jsonify
from flask_restful import Resource, reqparse
from processing import agent_checkin
from processing.user_role import authorized_groups

agent_checkin_parser = reqparse.RequestParser()
agent_checkin_parser.add_argument('Message')

class AgentCheckinEndpoint(Resource):
    @authorized_groups(['StandardRead', 'Transport'])
    def get(self, agent_name):
        print('[AgentCheckinEndpoint:GET] AgentID: %s' % (agent_name))
        task_obj = agent_checkin.process_agent_checkin(agent_name)
        return jsonify(task_obj)

    @authorized_groups(['StandardWrite', 'Transport'])
    def post(self, agent_name):
        args = agent_checkin_parser.parse_args()
        print('[AgentCheckinEndpoint:POST] AgentID: %s | Args: %s' % (agent_name, args))
        task_obj = agent_checkin.process_agent_checkin(agent_name, args['Message'])
        return jsonify(task_obj)