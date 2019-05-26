from flask import jsonify
from flask_restful import Resource, reqparse
from processing import agent_task
from logger import log


class AgentTaskEndpoint(Resource):
    def get(self, agent_task_id='all'):
        log("AgentCheckinEndpoint:GET", "AgentTaskId:  {0}".format(agent_task_id))
        tasks = agent_task.get_agent_task(agent_task_id)
        return jsonify(tasks)