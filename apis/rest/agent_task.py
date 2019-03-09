from flask import jsonify
from flask_restful import Resource, reqparse
from processing import agent_task


class AgentTaskEndpoint(Resource):
    def get(self, agent_task_id='all'):
        print('[AgentCheckinEndpoint:GET] AgentTaskId: %s' % (agent_task_id))
        tasks = agent_task.get_agent_task(agent_task_id)
        return jsonify(tasks)