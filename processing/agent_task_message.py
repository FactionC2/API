import base64
from backend.database import db

from sqlalchemy import and_

from models.agent import Agent
from models.agent_task_message import AgentTaskMessage
from logger import log


def agent_task_message_json(task_message):
    agent = Agent.query.get(task_message.AgentId)
    result = dict(
        {
            'AgentName' : agent.Name,
            'IV': task_message.IV,
            'HMAC': task_message.HMAC,
            'Message' : task_message.Message
         })
    return result


def agent_task_message_envelope_json(agent_name, encoded_messages):
    result = dict(
        {
            "AgentName": agent_name,
            "Message": encoded_messages.decode('utf8')
        }
    )
    return result


def get_unsent_agent_task_messages(agent_name):
    print('[get_unsent_task_messages] agent_id: %s ', agent_name)
    agent = Agent.query.filter_by(Name=agent_name).first()
    results = AgentTaskMessage.query.filter(and_(AgentTaskMessage.AgentId == agent.Id, AgentTaskMessage.Sent == False)).all()
    messages = ''
    log("get_unsent_task_messages", "got results: {}".format(str(results)))
    if len(results) != 0:
        messages = []
        for result in results:
            messages.append(agent_task_message_json(result))
            result.Sent = True
            db.session.add(result)
            db.session.commit()
    encoded_messages = base64.b64encode(str(messages).encode('utf-8'))
    response = agent_task_message_envelope_json(agent_name, encoded_messages)
    log("get_unsent_task_messages", "returning:  {}".format(response))
    return response
