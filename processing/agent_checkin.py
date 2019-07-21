from base64 import b64decode
from flask import json, request
from backend.rabbitmq import rabbit_producer
from models.agent_checkin import AgentCheckin
from processing import agent_task_message
from logger import log


def agent_checkin_json(agent_checkin):
    result = dict(
        {
            "AgentId": agent_checkin.AgentId,
            "IV": agent_checkin.IV,
            "HMAC": agent_checkin.HMAC,
            "Message": agent_checkin.Message
         })
    return result


def get_agent_checkin(agent_checkin_id='all'):
    if agent_checkin_id == 'all':
        result = []
        agent_messages = AgentCheckin.query.all()
        for agent_message in agent_messages:
            result.append(agent_checkin_json(agent_message))
    else:
        agent_message = AgentCheckin.query.get(agent_checkin_id)
        result = agent_checkin_json(agent_message)
    return result


def add_agent_checkin(agent_name, transport_id=None, source_ip=None, message=None):
    hmac = None
    iv = None
    msg = None
    if message:
        decoded_checkin = b64decode(message)
        checkin_dict = json.loads(decoded_checkin)
        hmac = checkin_dict["HMAC"]
        iv = checkin_dict["IV"]
        msg = checkin_dict["Message"]

    if not source_ip:
        source_ip = request.remote_addr

    if not transport_id:
        transport_id = 1

    checkin = {
        'AgentName': agent_name,
        'TransportId': transport_id,
        'SourceIp': source_ip,
        'HMAC': hmac,
        'IV': iv,
        'Message': msg
    }

    log("add_agent_task_response", "publishing?")
    rabbit_producer.send_request('NewAgentCheckin', checkin)
    return {
        'Success': True,
        'Result': checkin
    }


def process_agent_checkin(agent_name, transport_id=None, source_ip=None, message=None):
    result = add_agent_checkin(agent_name, transport_id, source_ip, message)
    return agent_task_message.get_unsent_agent_task_messages(agent_name)
