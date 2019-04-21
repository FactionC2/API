from flask_socketio import SocketIO, emit, join_room
from flask_login import current_user, login_required

from processing.user_role import authorized_groups
from processing import agent, agent_checkin, agent_task, console_message, \
    error_message, faction_file, ioc, payload, transport
from processing.user import logout_faction_user


socketio = SocketIO()


@socketio.on('connect')
@login_required
def connect_handler():
     if current_user.is_authenticated:
         print('[Socketio Connect Handler] User {0} authenticated'.format(current_user.Username))
         emit('{0} has connected'.format(current_user.Username), broadcast=True)


### AGENT API ###
@socketio.on('getAgent')
@authorized_groups(['StandardRead'])
def get_agent(data):
    print("[socketio.py - get_agent] starting for {0}..".format(current_user.Username))
    print("[socketio.py - get_agent] data: " + str(data))
    try:
        agent_id = data['AgentId']
    except:
        agent_id = 'all'
    results = agent.get_agent(agent_id, include_hidden=data.get('IncludeHidden'))
    print('Sending agent: ' + str(results))
    emit('getAgent', results)


@socketio.on('joinAgent')
@authorized_groups(['StandardRead'])
def join_agent(data):
    room = data['AgentId']
    print('Got join request for room ' + str(room))
    join_room(room)
    print('emitting..')
    emit('joinAgent', 'Joined room.', room=data['AgentId'])

@socketio.on('updateAgent')
@authorized_groups(['StandardWrite'])
def update_agent(data):
    response = agent.update_agent(data['AgentId'], data.get('Name'), data.get('Visible'))
    print('Agent ' + str(data['AgentId']) + ' updated')
    emit('updateAgent', response, broadcast=True)

@socketio.on('hideAgent')
@authorized_groups(['StandardWrite'])
def join_agent(data):
    response = agent.update_agent(data['AgentId'], visible=False)
    print('Agent ' + str(data['AgentId']) + ' updated')
    emit('updateAgent', response, broadcast=True)


### AGENT_CHECKIN API ####
@socketio.on('newAgentMessage')
@authorized_groups(['StandardWrite', 'Transport'])
def new_agent_message(data):
    print("[NewAgentMessage] Got: %s", str(data))
    message = agent_checkin.add_agent_checkin(data["AgentId"], data["Message"])
    emit('newAgentMessage', message)


### CONSOLE API ###
@socketio.on('getMessage')
@authorized_groups(['StandardRead'])
def get_message(data):
    print('[getMessage] getting message:' + str(data))
    message_obj = console_message.get_console_message(data)
    emit('getMessage', message_obj, room=data['AgentId'])

@socketio.on('getTaskMessage')
@authorized_groups(['StandardRead'])
def get_message(data):
    print('[getTaskMessage] getting message:' + str(data))
    message_obj = console_message.get_console_message_by_task(data['TaskId'])
    emit('getTaskMessage', message_obj)


@socketio.on('newMessage')
@authorized_groups(['StandardWrite'])
def new_message(data):
    print('[socketio:new_message] Got new message..' + str(data))
    console_message.new_console_message(data["AgentId"], data["Content"])

### ERROR MESSAGE API ###
@socketio.on('getErrorMessage')
@authorized_groups(['StandardRead'])
def get_error_message(data):
    print('[socketio:get_error_message] getting error message:' + str(data))
    error_messages = error_message.get_error_message(data.get('ErrorMessageId'))
    print('[socketio:get_error_message] getting error message:' + str(data))
    emit('getErrorMessage', error_messages)

### FILES API ###
@socketio.on('getFile')
@authorized_groups(['StandardRead'])
def get_faction_file(data):
    print('[socketio:get_faction_file] getting files:' + str(data))
    file_obj = faction_file.get_faction_file(data.get('Filename'))
    emit('getFile', file_obj)

### IOCs API ###
@socketio.on('getIOC')
@authorized_groups(['StandardRead'])
def get_message(data):
    print('[getIOC] getting ioc:' + str(data))
    ioc_obj = ioc.get_ioc(data['IocId'])
    emit('getIOC', ioc_obj)

### PAYLOADS API ###
@socketio.on('getPayload')
@authorized_groups(['StandardRead'])
def get_payload(data):
    print('[socketio:get_payload] getting payloads:' + str(data))
    payload_obj = payload.get_payload(data['PayloadId'], include_hidden=data.get('IncludeHidden'))
    emit('getPayload', payload_obj)


@socketio.on('newPayload')
@authorized_groups(['StandardWrite'])
def new_payload(data):
    print('[socketio:new_payload] req received')

    resp = payload.new_payload(description = data.get('Description'),
                               agent_type = data.get('AgentType'),
                               agent_transport_id = data.get('AgentTransportId'),
                               transport_id=data.get('TransportId'),
                               operating_system=data.get('OperatingSystemId'),
                               architecture=data.get('ArchitectureId'),
                               version=data.get('VersionId'),
                               format=data.get('FormatId'),
                               agent_type_configuration=data.get('AgentTypeConfigurationId'),
                               jitter = data.get('Jitter'),
                               interval = data.get('BeaconInterval'),
                               expiration_date = data.get('ExpirationDate'),
                               debug=data.get('Debug'))
    emit('newPayload', resp, broadcast=True)


@socketio.on('updatePayload')
@authorized_groups(['StandardWrite'])
def update_payload(data):
    print('[socketio:update_payload] req received')
    print(data)
    resp = payload.update_payload(
        payload_id=data.get('Id'),
        jitter=data.get("Jitter"),
        interval=data.get("Interval"),
        enabled=data.get("Enabled"),
        visible=data.get("Visible")
    )
    print(resp)
    emit('payloadUpdated', resp, broadcast=True)

@socketio.on('hidePayload')
@authorized_groups(['StandardWrite'])
def update_payload(data):
    print('[socketio:update_payload] req received')

    resp = payload.update_payload(
        payload_id=data.get('PayloadId'),
        enabled=False,
        visible=False
    )
    emit('payloadUpdated', resp, broadcast=True)

### TASKS API ###
@socketio.on('getTask')
@authorized_groups(['StandardRead'])
def get_task(data):
    print('[socketio:get_task] getting task: {0}'.format(data['TaskId']))
    task_obj = agent_task.get_agent_task(data['TaskId'])
    emit('getTask', task_obj)


### TRANSPORTS API ###
@socketio.on('getTransport')
@authorized_groups(['StandardRead'])
def get_transport(data):
    print('[socketio:get_transport] getting transports:' + str(data))
    transport_obj = transport.get_transport(data.get('TransportId'), include_hidden=data.get('IncludeHidden'))
    emit('getTransport', transport_obj)

@socketio.on('newTransport')
@authorized_groups(['StandardWrite'])
def new_transport(data):
    print('[socketio:new_transport] req received')
    resp = transport.new_transport(description=data.get('Description'))
    emit('transportCreated', resp)

@socketio.on('updateTransport')
@authorized_groups(['StandardWrite', 'Transport'])
def update_transport(data):
    print('[socketio:new_transport] req received')
    print('[socketio:update_transport] id: {0}'.format(data.get('TransportId')))
    print('[socketio:update_transport] Enabled: {0}'.format(data.get('Enabled')))
    response = transport.update_transport(transport_id=data.get('TransportId'),
                                        name=data.get('Name'),
                                        description=data.get('Description'),
                                        guid=data.get('Guid'),
                                        configuration=data.get('Configuration'),
                                        enabled=data.get('Enabled'),
                                        visible=data.get('Visible'))
    emit('transportUpdated', response, broadcast=True)

@socketio.on('hideTransport')
@authorized_groups(['StandardWrite'])
def update_transport(data):
    print('[socketio:new_transport] req received')
    print('[socketio:update_transport] id: {0}'.format(data.get('TransportId')))
    print('[socketio:update_transport] Enabled: {0}'.format(data.get('Enabled')))
    response = transport.update_transport(transport_id=data.get('TransportId'),
                                        enabled=False,
                                        visible=False)
    emit('transportUpdated', response, broadcast=True)

@socketio.on('logout')
@authorized_groups(['StandardRead'])
def logout():
    print('[socketio:logout] got logout request')
    response = logout_faction_user(current_user.Id)
    emit('loggedout', response)