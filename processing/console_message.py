from datetime import datetime
import json
import re

from flask_login import current_user
from models.console_message import ConsoleMessage
from models.agent import Agent
from models.agent_task import AgentTask
from models.user import User

from backend.rabbitmq import rpc_client
from processing.faction_file import get_faction_file_bytes
from logger import log


def console_message_json(message):
    if (message.UserId):
        user = User.query.get(message.UserId)
        username = user.Username
    elif (message.AgentId):
        agent = Agent.query.get(message.AgentId)
        username = agent.Name
    else:
        username = None

    result = dict(
        {
            'AgentId': message.AgentId,
            'UserId': message.UserId,
            'Username' : username,
            'Content' : message.Content,
            'Display': message.Display,
            'Type': message.Type,
            'Received'  : message.Received.isoformat()
         })
    return result


def new_console_message(agent_id, content):
    filenames = re.findall("(f2:files/[^\s]+)", content)
    display = content
    if len(filenames) > 0:
        for filename in filenames:
            name = filename.replace("f2:files/","")
            log("new_console_message", "getting bytes for file {0}".format(name))
            result = get_faction_file_bytes(name)
            if result['Success']:
                content = content.replace(filename, result['Message'])
            else:
                return dict({
                    'Success': False,
                    'Message': 'Could not find file: {0}'.format(filename)
                })
    console_message = {
        "AgentId": agent_id,
        "UserId": current_user.Id,
        "Content": content,
        "Display": display
    }

    log("add_message", "publishing message: {0}".format(console_message))
    rpc_client.send_request('NewConsoleMessage', console_message)
    return console_message

def get_console_message(console_message_id):
    if console_message_id == 'all':
        result = []
        console_messages = ConsoleMessage.query.all()
        for console_message in console_messages:
            result.append(console_message_json(console_message))
    else:
        console_message = ConsoleMessage.query.get(console_message_id)
        result = console_message_json(console_message)
    return result

def get_console_messages_by_agent(agent_id):
    agent = Agent.query.get(agent_id)
    if agent:
        console_messages = ConsoleMessage.query.filter_by(AgentId=agent_id)
        results = []
        for message in console_messages:
            results.append(console_message_json(message))
        return {
            "Success": True,
            "Results": results
        }
    else:
        return {
            "Success": False,
            "Message": "No agent found with id: {0}".format(agent_id)
        }


def get_console_message_by_task(agent_task_id):
    task = AgentTask.query.get(agent_task_id)
    if task:
        console_messages = ConsoleMessage.query.filter_by(AgentTaskId=agent_task_id)
        results = []
        if console_messages.count() > 0:
            log("get_console_message_by_task", "Got count. Going.")
            for message in console_messages:
                log("get_console_message_by_task", "Working on: {0}".format(message))
                results.append(console_message_json(message))
        return {
            "Success": True,
            "Results": results
        }
    else:
        return {
            "Success": False,
            "Message": "No agent found with id: {0}".format(agent_task_id)
        }

