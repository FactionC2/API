from base64 import b64decode
import time
import pika
from datetime import datetime
from time import sleep
import threading
import json
import amqpstorm
from amqpstorm import Message
from flask_socketio import SocketIO
from config import RABBIT_HOST, RABBIT_URL, RABBIT_USERNAME, RABBIT_PASSWORD


class RpcClient(object):
    """Asynchronous Rpc client."""

    def __init__(self, host, username, password, rpc_queue):
        print('[AMPQSTORM:open] Creating client..')
        self.queue = {}
        self.host = host
        self.username = username
        self.password = password
        self.channel = None
        self.connection = None
        self.rpc_queue = rpc_queue
        self.callback_queue = None
        self.socketio = SocketIO(message_queue=RABBIT_URL, channel="ConsoleMessages")
        self.open()

    def open(self):
        """Open Connection."""
        rabbit_connected = False
        print('[AMPQSTORM:open] Opening Connection..')
        print("[AMPQSTORM:open] Checking RabbitMQ..")
        while not rabbit_connected:
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
                                                                               credentials=credentials,
                                                                               socket_timeout=2,
                                                                               blocked_connection_timeout=2))
                rabbit_connected = True
                print("[AMPQSTORM:open] RabbitMQ is up!")
                connection.close()
            except:
                rabbit_connected = False
                print("[AMPQSTORM:open] RabbitMQ not reachable.. waiting..")
                sleep(2)

        self.connection = amqpstorm.Connection(self.host, self.username,
                                               self.password)
        self.channel = self.connection.channel()

        # Create the exchange
        self.exchange = amqpstorm.channel.Exchange(self.channel)
        self.exchange.declare(exchange='Core',
                              exchange_type='topic',
                              durable=True)

        # Create the APIService queue
        print('[AMPQSTORM:open] Creating queue: ' + self.rpc_queue)
        self.channel.queue.declare(self.rpc_queue, durable=True, exclusive=False, auto_delete=False, arguments=None)
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='Agent')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='AgentTaskUpdate')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='AgentCheckinAnnouncement')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='ConsoleMessageAnnouncement')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='AgentUpdated')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='ErrorMessageAnnouncement')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='NewFactionFile')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='PayloadUpdate')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='PayloadUpdated')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='TransportUpdated')
        self.channel.basic.consume(self._on_response, no_ack=True, queue=self.rpc_queue)

        # Create Callback queue
        result = self.channel.queue.declare(exclusive=True)

        print('[AMPQSTORM:open] Creating callback queue: ' + result['queue'])
        self.callback_queue = result['queue']
        self.channel.basic.consume(self._on_response, no_ack=True,
                                   queue=self.callback_queue)

        self._create_process_thread()

    def _create_process_thread(self):
        """Create a thread responsible for consuming messages in response
         to RPC requests.
        """

        print('[AMPQSTORM:_create_process_thread] Creating Thread..')
        thread = threading.Thread(target=self._process_data_events)
        thread.setDaemon(True)
        thread.start()

    def _process_data_events(self):
        """Process Data Events using the Process Thread."""

        print('[AMPQSTORM:_process_data_events] Consuming..')
        self.channel.start_consuming()

    def _on_response(self, message):
        """On Response store the message with the correlation id in a local
         dictionary.
        """
        # TODO: This could be more nuanced, but who has time for that.
        try:
            print('[AMPQSTORM:_on_response] Message Properties: ' + json.dumps(message.properties))
            print('[AMPQSTORM:_on_response] Message Body: ' + message.body)

            if message.correlation_id in self.queue:
                print('[AMPQSTORM:_on_response] Got a response to one of our messages. Updating queue.')
                self.queue[message.correlation_id] = message.body

            elif message.properties['message_type'] == 'Agent':
                print("[AMPQSTORM:_on_response] Got Agent at {0}".format(message.timestamp))
                agent = json.loads(message.body)
                agent['Success'] = True
                print("[AMPQSTORM:_on_response] Publishing message: {0}".format(str(agent)))
                self.socketio.emit('newAgent', agent, broadcast=True)

            elif message.properties['message_type'] == 'AgentCheckinAnnouncement':
                print("[AMPQSTORM:_on_response] Got AgentCheckinAnnouncement at {0}".format(message.timestamp))
                agentCheckin = json.loads(message.body)
                print("[AMPQSTORM:_on_response] Publishing message: {0}".format(str(agentCheckin)))
                self.socketio.emit('agentCheckin', agentCheckin)

            elif message.properties['message_type'] == 'AgentUpdated':
                print("[AMPQSTORM:_on_response] Got AgentCheckin at {0}".format(message.timestamp))
                agentUpdated = json.loads(message.body)
                print("[AMPQSTORM:_on_response] Publishing message: {0}".format(str(agentUpdated)))
                self.socketio.emit('agentUpdated', agentUpdated)

            elif message.properties['message_type'] == 'ConsoleMessageAnnouncement':
                print("[AMPQSTORM:_on_response] Got ConsoleMessageAnnouncement")
                message = json.loads(message.body)
                consoleMessage = message['ConsoleMessage']
                consoleMessage['Username'] = message['Username']
                consoleMessage.pop('Content', None)
                print("[AMPQSTORM:_on_response] Publishing message: {0}".format(str(consoleMessage)))
                self.socketio.emit('consoleMessageAnnouncement', consoleMessage, room=consoleMessage["AgentId"])

            elif message.properties['message_type'] == 'ErrorMessageAnnouncement':
                print("[AMPQSTORM:_on_response] Got ErrorMessageAnnouncement at {0}".format(message.timestamp))
                errorMessageAnnouncement = json.loads(message.body)
                print("[AMPQSTORM:_on_response] Publishing message: {0}".format(str(errorMessageAnnouncement)))
                # TL;DR - We only broadcast errors if they didn't come from API
                # I *think* this is the right way to go about this. API errors shouldn't typically be of interest to
                # everyone using Faction and the API is going to reply back with the error message when it encounters
                # it.
                if errorMessageAnnouncement['Source'] != 'API':
                    self.socketio.emit('errorMessageAnnouncement', errorMessageAnnouncement)
                else:
                    self.socketio.emit('errorMessageAnnouncement', errorMessageAnnouncement, broadcast=True)

            elif message.properties['message_type'] == 'NewFactionFile':
                print("[AMPQSTORM:_on_response] Got NewFactionFile")
                fileMessage = json.loads(message.body)
                print("[AMPQSTORM:_on_response] Emitting: " + message.body)
                self.socketio.emit('newFile', fileMessage)

            elif message.properties['message_type'] == 'NewTransport':
                print("[AMPQSTORM:_on_response] Got PayloadUpdate")
                transportMessage = json.loads(message.body)
                print("[AMPQSTORM:_on_response] Emitting: " + message.body)
                self.socketio.emit('newTransport', transportMessage)

            elif message.properties['message_type'] == 'PayloadUpdate':
                print("[AMPQSTORM:_on_response] Got PayloadUpdate")
                payloadUpdateMessage = json.loads(message.body)
                print("[AMPQSTORM:_on_response] Emitting: " + message.body)
                self.socketio.emit('updatePayload', payloadUpdateMessage)

            elif message.properties['message_type'] == 'PayloadUpdated':
                print("[AMPQSTORM:_on_response] Got PayloadUpdate")
                payloadUpdateMessage = json.loads(message.body)
                print("[AMPQSTORM:_on_response] Emitting: " + message.body)
                self.socketio.emit('payloadUpdated', payloadUpdateMessage)


            elif message.properties['message_type'] == 'TransportCreated':
                print("[AMPQSTORM:_on_response] Got TransportCreated")
                transportMessage = json.loads(message.body)
                print("[AMPQSTORM:_on_response] Emitting: " + message.body)
                self.socketio.emit('transportCreated', transportMessage)

            elif message.properties['message_type'] == 'TransportUpdated':
                print("[AMPQSTORM:_on_response] Got TransportUpdated")
                transportMessage = json.loads(message.body)
                print("[AMPQSTORM:_on_response] Emitting: " + message.body)
                self.socketio.emit('transportUpdated', transportMessage)

            elif message.properties['message_type'] == 'AgentCheckinAnnouncement':
                print("[AMPQSTORM:_on_response] Got AgentCheckinAnnouncement!")

            elif message.properties['message_type'] == 'AgentTaskUpdate':
                print("[AMPQSTORM:_on_response] Got AgentTaskUpdate")
        except Exception as e:
            print("[AMPQSTORM:_on_response] ERROR PROCESSING RABBITMQ MESSAGE: {0}".format(e))

            # cmd_obj = json.loads(message.body)
            # cmd_obj['Username'] = 'AGENT'
            # print('[AMPQSTORM] emitting. AgentId ' + str(cmd_obj['AgentId']) + ' Body: ' + message.body)
            # self.socketio.emit('newMessage', cmd_obj, room=cmd_obj['AgentId'])
        # else:
        #     print('[AMPQSTORM] Not for us.. nacking..')
        #     message.nack()

    def send_request(self, routing_key, message, callback=False):
        # Create the Message object.
        print("[AMPQSTORM:send_request] Got message: {0} with routing_key: {1}".format(message, routing_key))
        message = Message.create(self.channel, json.dumps(message))


        if callback:
            message.reply_to = self.callback_queue
            self.queue[message.correlation_id] = None
        # Create an entry in our local dictionary, using the automatically
        # generated correlation_id as our key.


        message.properties['message_type'] = routing_key

        # Publish the RPC request.
        print("[AMPQSTORM:send_request] Publishing message..")
        message.publish(routing_key=routing_key, exchange='Core')

        # Return the Unique ID used to identify the request.

        print("[AMPQSTORM:send_request] Got correlation_id: {0}".format(str(message.correlation_id)))
        return message.correlation_id


rpc_client = RpcClient(RABBIT_HOST, RABBIT_USERNAME, RABBIT_PASSWORD, 'ApiService')