from flask import json

from models.agent import Agent
from models.staging_message import StagingMessage
from backend.database import db
from backend.rabbitmq import rpc_client


def agent_json(agent):
    print("[agent_json] Working on %s" % agent)
    tasks = []
    # if agent.tasks:
    #     for task in agent.tasks:
    #         json_task = dict({'task_id': task.Id, 'agent_id': task.AgentId, 'command': task.Command, 'results': task.Results})
    #         tasks.append(json_task)

    agentType = dict({
        "Id": agent.AgentType.Id,
        "Name": agent.AgentType.Name
    })

    result = {
        'Id': agent.Id,
        'Name': agent.Name,
        'Username': agent.Username,
        'Hostname': agent.Hostname,
        'Pid': agent.PID,
        'AgentType': agentType,
        'Admin': agent.Admin,
        'OperatingSystem': agent.OperatingSystem,
        'InitialCheckin': agent.InitialCheckin.isoformat(),
        'LastCheckin': agent.LastCheckin.isoformat(),
        'InternalIP': agent.InternalIP,
        'ExternalIP': agent.ExternalIP,
        'Visible': agent.Visible
    }
    return result

def get_agent(agent_id, include_hidden=False):
    print("[get_agent] got agent id " + str(agent_id))
    if agent_id == 'all':
        if include_hidden:
            agents = Agent.query.all()
        else:
            agents = Agent.query.filter_by(Visible=True)
        result = []
        for agent in agents:
            result.append(agent_json(agent))
    else:
        agent = Agent.query.get(agent_id)
        result = agent_json(agent)
    return result


def update_agent(agent_id, agent_name=None, visible=None):
    agent = Agent.query.get(agent_id)
    if agent_name:
        agent.Name = agent_name

    if visible is not None:
        agent.Visible = visible

    message = dict({
        "Id": agent_id,
        "Name": agent.Name,
        "Visible": agent.Visible
    })
    print("[update_agent] sending message: {0}".format(message))
    rpc_client.send_request("UpdateAgent", message)
    return {"Success": True, "Result": agent_json(agent)}