from datetime import datetime

from flask import json
from flask_socketio import SocketIO
from backend.rabbitmq import rpc_client

from models.agent import Agent
from models.ioc import IOC
from models.user import User
from models.console_message import ConsoleMessage

def ioc_json(ioc):
    if (ioc.UserId):
        username = (User.query.get(ioc.UserId)).Username
    else:
        username = "None"

    agent = {
        "Id": ioc.AgentTaskUpdate.AgentTask.AgentId,
        "Name": ioc.AgentTaskUpdate.AgentTask.Agent.Name,
        "Hostname": ioc.AgentTaskUpdate.AgentTask.Agent.Hostname,
        "InternalIPAddress": ioc.AgentTaskUpdate.AgentTask.Agent.InternalIP
    }

    console_message_object = ConsoleMessage.query.filter_by(AgentTaskId=ioc.AgentTaskUpdate.AgentTask.Id)\
        .filter_by(Type="AgentTask").first()

    console_message = {
        "Id": console_message_object.Id,
        "Display": console_message_object.Display,
        "UserId": console_message_object.UserId
    }

    hash = None
    if ioc.Hash:
        hash = ioc.Hash

    result = {
        "Id": ioc.Id,
        "Agent": agent,
        "ConsoleMessage": console_message,
        "Action": ioc.Action,
        "Description": ioc.Description,
        "Timestamp": ioc.Timestamp.isoformat(),
        "Identifier": ioc.Identifier,
        "Hash": ioc.Hash,
        "Type": ioc.Type,
        "Username": username
    }
    return result

def get_ioc(ioc_id='all'):
    iocs = []
    results = []
    print("Got IOC: {0}".format(ioc_id))
    if ioc_id == 'all':
        iocs = IOC.query.all()
    else:
        iocs.append(IOC.query.get(ioc_id))

    if len(iocs) > 0:
        for ioc in iocs:
            results.append(ioc_json(ioc))
        return {
            "Success": True,
            "Results": results
        }
    else:
        return {
            "Success": False,
            "Message": "No IOCs found matching id: {0}".format(ioc_id)
        }
