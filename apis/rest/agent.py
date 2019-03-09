from flask import jsonify, request
from flask_restful import Resource, fields, reqparse
from processing import agent, agent_checkin
from processing.user_role import authorized_groups

task_fields = {
    'id': fields.Integer,
    'agent_id': fields.Integer,
    'command': fields.String,
    'results': fields.String
}

agent_fields = {
    'id': fields.Integer,
    'tasks': fields.List(fields.Nested(task_fields))
}


# These parsers take arguments from a rest request and parse them

agent_parser = reqparse.RequestParser()
agent_parser.add_argument('Name')
agent_parser.add_argument('Enabled')


class AgentEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, agent_id='all'):
        include_hidden = request.args.get("include_hidden")
        agent_obj = agent.get_agent(agent_id, include_hidden)
        return jsonify(agent_obj)


    @authorized_groups(['StandardWrite'])
    def put(self, agent_id):
        args = agent_parser.parse_args()
        response = agent.update_agent(agent_id, agent_name=args.get('Name'), visible=args.get('Visible'))
        return jsonify(response)

    @authorized_groups(['StandardWrite'])
    def delete(self, agent_id):
        response = agent.update_agent(agent_id, visible=False)
        return jsonify(response)
