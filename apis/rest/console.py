from flask import jsonify
from flask_restful import Resource, reqparse
from processing import console_message
from processing.user_role import authorized_groups
from logger import log

console_parser = reqparse.RequestParser()
console_parser.add_argument('AgentId')
console_parser.add_argument('Content')


class ConsoleEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, console_message_id):
        response = console_message.get_console_message(console_message_id)
        return jsonify(response)


class ConsoleAgentEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, agent_id):
        log("ConsoleAgentEndpoint", "Got request for agent_id: {0}".format(agent_id))
        response = console_message.get_console_messages_by_agent(agent_id)
        return jsonify(response)

    @authorized_groups(['StandardWrite'])
    def post(self):
        args = console_parser.parse_args()
        log("ConsoleEndpoint", "Got args: {}".format(args))
        response = console_message.new_console_message(args.get("AgentId"), args.get("Content"))
        return jsonify(response)
    

class ConsoleTaskEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, agent_task_id):
        log("ConsoleTaskEndpoint", "Got request for task_id: {0}".format(agent_task_id))
        response = console_message.get_console_message_by_task(agent_task_id)
        return jsonify(response)