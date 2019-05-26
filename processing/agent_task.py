from datetime import datetime

from flask import json
from flask_socketio import SocketIO
from backend.rabbitmq import rabbit_producer

from models.agent import Agent
from models.agent_task import AgentTask
from models.console_message import ConsoleMessage
from models.user import User

def agent_task_json(agent_task):
    updates = []
    complete = False
    success = False
    for update in agent_task.AgentTaskUpdates:
        if update.Success:
            success = True

        if update.Complete:
            complete = True

        updates.append({
            "Complete": update.Complete,
            "Success": update.Success,
            "Message": update.Message,
            "Received": update.Received.isoformat()
        })
    console_message = ConsoleMessage.query.filter_by(AgentTaskId=agent_task.Id).first()
    if (console_message and console_message.UserId):
        user = (User.query.get(console_message.UserId)).Username
    else:
        user = "None"

    agent = Agent.query.get(agent_task.AgentId)
    agentName = agent.Name
    result = {
        "Id": agent_task.Id,
        "AgentId": agent_task.AgentId,
        "AgentName": agentName,
        "Action": agent_task.Action,
        "Created": agent_task.Created.isoformat(),
        "Command": agent_task.Command,
        "Username": user,
        "Updates": updates,
        "Complete": complete,
        "Success": success
    }
    return result

def get_agent_task(agent_task_id='all'):
    agent_tasks = []
    results = []
    if agent_task_id == 'all':
        agent_tasks = AgentTask.query.all()
    else:
        agent_tasks.append(AgentTask.query.get(agent_task_id))

    if len(agent_tasks) > 0:
        for agent_task in agent_tasks:
            results.append(agent_task_json(agent_task))
        return {
            "Success": True,
            "Results": results
        }
    else:
        return {
            "Success": False,
            "Message": "No agent tasks found matching id: {0}".format(agent_task_id)
        }




