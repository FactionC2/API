from flask import jsonify, request
from flask_restful import Resource, reqparse
from processing import agent_checkin
from processing.user_role import authorized_groups
from logger import log


agent_checkin_parser = reqparse.RequestParser()
agent_checkin_parser.add_argument('TransportId')
agent_checkin_parser.add_argument('SourceIP')
agent_checkin_parser.add_argument('Message')

class AgentCheckinEndpoint(Resource):
    @authorized_groups(['StandardRead', 'Transport'])
    def get(self, agent_name):
        log("AgentCheckinEndpoint:GET", "AgentID:  {0}".format(agent_name))
        task_obj = agent_checkin.process_agent_checkin(agent_name=agent_name,
                                                       transport_id=request.args.get('TransportId'),
                                                       source_ip=request.args.get('SourceIp'))
        return jsonify(task_obj)

    @authorized_groups(['StandardWrite', 'Transport'])
    def post(self, agent_name):
        args = agent_checkin_parser.parse_args()
        log("AgentCheckinEndpoint:POST", "AgentID: %s | Args:  {0}".format(agent_name, args))
        task_obj = agent_checkin.process_agent_checkin(agent_name=agent_name,
                                                       transport_id=args.get('TransportId'),
                                                       source_ip=args.get('SourceIp'),
                                                       message=args.get('Message'))
        return jsonify(task_obj)