from base64 import b64encode, b64decode
from time import sleep
from flask import json

from models.agent import Agent
from models.staging_message import StagingMessage
from models.staging_response import StagingResponse

from processing.agent import get_agent

from backend.rabbitmq import rpc_client


def staging_message_json(staging_message):
    print("[staging_message_json] Working on %s" % staging_message)
    tasks = []
    # if staging_message.tasks:
    #     for task in staging_message.tasks:
    #         json_task = dict({'task_id': task.Id, 'agent_id': task.AgentId, 'command': task.Command, 'results': task.Results})
    #         tasks.append(json_task)
    result = dict({
        'PayloadName': staging_message.PayloadName,
        'IV': staging_message.IV,
        'HMAC': staging_message.HMAC,
        'Message': staging_message.Message
    })
    return result

def staging_response_json(staging_response):
    result = dict({
        'AgentName' : staging_response.AgentName,
        'IV': staging_response.IV,
        'HMAC': staging_response.HMAC,
        'Message' : staging_response.Message
    })
    return result

def staging_response_envelope(agentName, message):
    result = dict({
        'Success': True,
        "AgentName": agentName,
        "Message": message
    })
    return result

def get_staging_response(staging_id):
    response = None
    agent = Agent.query.filter_by(StagingId=staging_id).first()
    if agent and agent.StagingResponseId:
        response = StagingResponse.query.filter_by(Id=agent.StagingResponseId).filter_by(Sent=False).last()
    if response:
        response_json = staging_message_json(response)
        results = []
        results.append(response_json)
        encoded_message = b64encode(str(results).encode('utf-8'))
        staging_envelope = staging_response_envelope(agent.Name, encoded_message)

        return results
    return dict({
        "Success":False,
        "Message": "No staging response available for ID: {0}".format(staging_id)
    })


# TODO: This should be handled by core
def new_staging_message(payload_name, staging_id, message):
    print("[staging_message:new_staging_message] Got staging request. PayloadName: {0} ID: {1}".format(payload_name, staging_id))

    response = get_staging_response(staging_id)
    if response['Success']:
        return response
    else:
        decoded_response = b64decode(message)
        response_dict = json.loads(decoded_response)
        staging_message = StagingMessage()
        staging_message.PayloadName = payload_name
        staging_message.IV = response_dict['IV']
        staging_message.HMAC = response_dict['HMAC']
        staging_message.Message = response_dict['Message']
        staging_msg_json = staging_message_json(staging_message)

    print("[staging_message:new_staging_message] Publishing: {0}".format(staging_msg_json))
    message_id = rpc_client.send_request('StagingMessage', staging_msg_json, callback=True)

    # Wait for our response
    print("[staging_message:new_staging_message] Waiting for 60 seconds")
    i = 0
    while rpc_client.queue[message_id] is None and i < 60:
        print("[staging_message:new_staging_message] Waiting for {0} seconds".format(60 - i))
        sleep(1)
        i += 1

    # Return data
    message = rpc_client.queue[message_id]

    if message:
        print("[staging_message] Got response from Core: {0}".format(message))
        return json.loads(message)
    else:
        print("[staging_message] Timed out.")
        return "ERROR"
