import os
import dateparser
from time import sleep
from datetime import datetime
from secrets import token_urlsafe

from flask import json, request
from itsdangerous import URLSafeSerializer
from werkzeug.utils import secure_filename

from processing.error_message import create_error_message

from backend.database import db

from backend.rabbitmq import rabbit_consumer
from backend.rabbitmq import rabbit_producer

from config import UPLOAD_DIR, SECRET_KEY
from models.payload import Payload
from logger import log

payload_upload_dir = os.path.join(UPLOAD_DIR, 'payloads/')


def payload_json(payload):
    log("payload_json", "Working on %s" % payload)

    lastDownloaded = None
    if payload.LastDownloaded:
        lastDownloaded = payload.LastDownloaded.isoformat()

    expirationDate = None
    if payload.ExpirationDate:
        expirationDate = payload.ExpirationDate.isoformat()

    agentType = dict({
        'Id': payload.AgentType.Id,
        'Name': payload.AgentType.Name
    })

    operating_system = dict({
        'Id': payload.AgentTypeOperatingSystem.Id,
        'Name': payload.AgentTypeOperatingSystem.Name
    })

    architecture = dict({
        'Id': payload.AgentTypeArchitecture.Id,
        'Name': payload.AgentTypeArchitecture.Name
    })

    configuration = dict({
        'Id': payload.AgentTypeConfiguration.Id,
        'Name': payload.AgentTypeConfiguration.Name
    })

    agentTypeFormat = dict({
        'Id': payload.AgentTypeFormat.Id,
        'Name': payload.AgentTypeFormat.Name
    })

    agentTransport = dict({
        'Id': payload.AgentTransportType.Id,
        'Name': payload.AgentTransportType.Name
    })

    transport = dict({
        'Id': payload.Transport.Id,
        'Name': payload.Transport.Name,
        'TransportType': payload.Transport.TransportType
    })

    result = {
        'Id': payload.Id,
        'Name': payload.Name,
        'Description': payload.Description,
        'Key': payload.Key,
        'AgentType': agentType,
        'Configuration': configuration,
        'Architecture': architecture,
        'OperatingSystem': operating_system,
        'Format': agentTypeFormat,
        'AgentTransport': agentTransport,
        'Transport': transport,
        'Created': payload.Created.isoformat(),
        'Built': payload.Built,
        'LastDownloaded': lastDownloaded,
        'BeaconInterval': payload.BeaconInterval,
        'Jitter': payload.Jitter,
        'ExpirationDate': expirationDate,
        'Enabled': payload.Enabled,
        'Visible': payload.Visible
    }
    log("payload_json", "returning {0}".format(result))
    return result


def get_payload(payload_id, include_hidden=False):
    log("get_payload", "got payload id " + str(payload_id) + ", show hidden: " + str(include_hidden))
    if payload_id == 'all':
        if include_hidden:
            payloads = Payload.query.all()
        else:
            payloads = Payload.query.filter_by(Visible=True)
        result = []
        for payload in payloads:
            result.append(payload_json(payload))
    else:
        payload = Payload.query.get(payload_id)
        result = payload_json(payload)
    return dict({
        'Results': result,
        'Success': True
    })


def new_payload(description,
                agent_type,
                transport_id,
                agent_transport_id,
                operating_system,
                architecture,
                version,
                format,
                agent_type_configuration,
                jitter,
                interval,
                debug,
                expiration_date=None):

    log("payload:new_payload", "Got request")
    log("payload:new_payload", "Details - Jitter: {0}, Interval: {1}, AgentType: {2}, ExpirationDate: {3}".format(jitter, interval, agent_type, expiration_date))

    if expiration_date != None:
        try:
            expiration_date = dateparser.parse(expiration_date).isoformat()
        except:
            error_message = create_error_message("Could not convert {0} to a DateTime object".format(expiration_date))
            return error_message

    if jitter is None:
        jitter_float = None
    else:
        try:
            jitter_float = float(jitter)
        except:
            error_message = create_error_message("Jitter is in invalid format. Expected 0.0 to 1.0. Got {0}".format(jitter))
            return error_message

    error_at = None
    expected = None

    if not isinstance(transport_id, int):
        error_at = "TransportId"
        expected = "Expected an Integer."

    if not isinstance(agent_transport_id, int):
        error_at = "AgentTransportId"
        expected = "Expected an Integer."

    if not isinstance(interval, int):
        error_at = "BeaconInterval"
        expected = "Expected an Integer."

    if jitter_float is not None and 1.0 < jitter_float < 0.0:
        error_at = "Jitter"
        expected = "Expected 0.0 to 1.0."

    if error_at is not None:
        error_message = create_error_message("Error processing {0}. {1}".format(error_at, expected))
        return error_message


    payload_name = token_urlsafe(8)
    s = URLSafeSerializer(SECRET_KEY)
    build_token = s.dumps(payload_name)

    publish_message = dict({
        "Name": payload_name,
        "Description": description,
        "BuildToken": build_token,
        "AgentTypeId": agent_type,
        "AgentTransportTypeId": agent_transport_id,
        "TransportId": transport_id,
        "OperatingSystemId": operating_system,
        "ArchitectureId": architecture,
        "VersionId": version,
        "FormatId": format,
        "AgentTypeConfigurationId": agent_type_configuration,
        "Jitter": "{0:0.1f}".format(jitter_float),
        "BeaconInterval": interval,
        "ExpirationDate": expiration_date,
        "Debug": debug
    })

    log("payload:new_payload", "Publishing: {0}".format(publish_message))
    message_id = rabbit_producer.send_request("NewPayload", publish_message)
    #
    # # Wait for our response
    # # TODO: Add actual timeout here.
    # i = 0
    # while rabbit_consumer.queue[message_id] is None and i < 15:
    #     log("payload:new_payload", "Waiting for {0} seconds".format(15 - i))
    #     sleep(1)
    #     i += 1
    #
    # # Return data
    # message = rabbit_consumer.queue[message_id]
    #
    # if message:
    #     log("payload:new_payload", "Got response from Build Server: {0}".format(message))
    #     message_dict = json.loads(message)
    #     if message_dict.get('Source'):
    #         log("payload:new_payload", "Its an error..")
    #         return message_dict
    #     else:
    #         payload = Payload.query.get(message_dict['Id'])
    #         return {
    #             "Success": True,
    #             "Result": payload_json(payload)
    #         }
    # log("payload:new_payload", "Timed out.")
    # return create_error_message("Timeout waiting for response from Core while processing new payload")


def update_payload(payload_id, enabled=None, jitter=None, interval=None, visible=None, expiration_date=None):
    payload = Payload.query.get(payload_id)
    if jitter:
        payload.Jitter = jitter
    if interval:
        payload.BeaconInterval = interval
    if expiration_date:
        payload.ExpirationDate = expiration_date
        expiration_date = payload.ExpirationDate.isoformat()
    if enabled is not None:
        payload.Enabled = enabled
    if visible is not None:
        payload.Visible = visible

    message = dict({
        "Id": payload_id,
        "Jitter": payload.Jitter,
        "BeaconInterval": payload.BeaconInterval,
        "ExpirationDate": expiration_date,
        "Enabled": payload.Enabled,
        "Visible": payload.Visible
    })

    log("payload.py:update_payload", "Sending: {0}".format(message))
    rabbit_producer.send_request("UpdatePayload", message)
    return dict({"Success": True, "Payload": payload_json(payload)})


# PAYLOAD FILE STUFF #
def upload_payload(payload_id, build_token):
    log("payload:upload_payload", "Got id: {0} with token: {1}".format(str(payload_id), build_token))
    payload = Payload.query.get(payload_id)
    s = URLSafeSerializer(SECRET_KEY)
    token_value = s.loads(build_token)
    log("payload:upload_payload", "token value: {0}".format(token_value))
    if payload.Filename == None and payload.Name == token_value:
        log("payload:upload_payload", "filename is null and token matches")
        payload.Built = True
        file = request.files['file']
        payload.Filename = secure_filename(file.filename)
        log("payload:upload_payload", "filename set to: {0}".format(payload.Filename))
        try:
            savePath = os.path.join(payload_upload_dir, payload.Filename)
            log("payload:upload_payload", "saving file to: {0}".format(savePath))
            file.save(savePath)
            db.session.add(payload)
            db.session.commit()

            payload_message = dict({
                "Success": True,
                "Payload": payload_json(payload)
            })

            rabbit_producer.send_request('PayloadUpdated', payload_message)

            return dict({
                'Success': True,
                'Message': 'File saved as {0}'.format(payload.Filename)
            })
        except Exception as e:
            log("payload:upload_payload", "file save failed: {0}".format(str(e)))
            return create_error_message('Failed to save file: {0}'.format(str(e)))
    else:
        log("payload:upload_payload", "token check failed or payload already built")
        return create_error_message('Payload token invalid or payload already built')


def download_payload(payload_id):
    payload = Payload.query.get(payload_id)
    if payload.Filename:
        path = os.path.join(payload_upload_dir, payload.Filename)
        log("payload:download_payload", "returning path: {0}".format(path))
        payload.LastDownloaded = datetime.utcnow()
        db.session.add(payload)
        db.session.commit()

        return dict({
            'Success': True,
            'Message': path,
            'Filename': payload.Filename
        })
    else:
        return dict({
            'Success': False,
            'Message': 'Payload file does not exist'
        })
