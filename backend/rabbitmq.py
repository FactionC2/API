import pika
from time import sleep
import json
import amqpstorm
from amqpstorm import Message
from config import RABBIT_HOST, RABBIT_USERNAME, RABBIT_PASSWORD
from logger import log


class Consumer(object):
    """Asynchronous Rpc client."""

    def __init__(self):
        log('rabbitmq-consumer:init', 'Creating client..')
        self.queue = {}
        self.host = RABBIT_HOST
        self.username = RABBIT_USERNAME
        self.password = RABBIT_PASSWORD
        self.channel = None
        self.connection = None
        self.callback_queue = None
        self.rpc_queue = 'ApiService'
        self.socketio = None
        self.open()

    def open(self):
        """Open Connection."""
        rabbit_connected = False
        log('rabbitmq-consumer:open', 'Opening Connection..')
        log("rabbitmq-consumer:open", "Checking RabbitMQ..")
        while not rabbit_connected:
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
                                                                               credentials=credentials,
                                                                               socket_timeout=2,
                                                                               blocked_connection_timeout=2))
                rabbit_connected = True
                log("rabbitmq-consumer:open", "RabbitMQ is up!")
                connection.close()
            except Exception as e:
                rabbit_connected = False
                log("rabbitmq-consumer:open", f"Connection Error: {str(e)}")
                log("rabbitmq-consumer:open", "RabbitMQ not reachable.. waiting..")
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
        log('rabbitmq-consumer:open', 'Creating queue:  {0}'.format(self.rpc_queue))
        self.channel.queue.declare(self.rpc_queue, durable=True, exclusive=False, auto_delete=False, arguments=None)
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='AgentCheckinAnnouncement')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='AgentCommandsUpdated')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='AgentTaskUpdate')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='AgentUpdated')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='ConsoleMessageAnnouncement')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='DevPayloadCreated')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='ErrorMessageAnnouncement')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='NewFactionFile')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='NewAgent')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='PayloadCreated')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='PayloadUpdated')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='TransportCreated')
        self.channel.queue.bind(self.rpc_queue, exchange='Core', routing_key='TransportUpdated')
        self.channel.basic.consume(self._on_response, no_ack=True, queue=self.rpc_queue)

        # Create Callback queue
        result = self.channel.queue.declare(exclusive=True)

        log("rabbitmq-consumer:open", "Creating callback queue: {}".format(result['queue']))
        self.callback_queue = result['queue']
        self.channel.basic.consume(self._on_response, no_ack=True,
                                   queue=self.callback_queue)

    #     self._create_process_thread()
    #
    # def _create_process_thread(self):
    #     """Create a thread responsible for consuming messages in response
    #      to RPC requests.
    #     """
    #
    #     log("rabbitmq-consumer:_create_process_thread", "Creating Thread..")
    #     thread = threading.Thread(target=self._process_data_events)
    #     thread.setDaemon(True)
    #     thread.start()
        return self

    def update_queue(self, message_id):
        log("rabbitmq-consumer:update_queue", "Adding message id: {}".format(message_id))
        self.queue[message_id] = None

    def process_data_events(self):
        """Process Data Events using the Process Thread."""

        log("rabbitmq-consumer:_process_data_events", "Consuming..")
        self.channel.start_consuming()

    def _on_response(self, message):
        """On Response store the message with the correlation id in a local
         dictionary.
        """
        # TODO: This could be more nuanced, but who has time for that.
        try:
            log('rabbitmq-consumer:_on_response', 'Message Properties:  {0}'.format(json.dumps(message.properties)))
            log('rabbitmq-consumer:_on_response', 'Message Body:  {0}'.format(message.body))

            if message.correlation_id in self.queue:
                log('rabbitmq-consumer:_on_response', 'Got a response to one of our messages. Updating queue.')
                self.queue[message.correlation_id] = message.body

            # AGENT CHECKIN ANNOUNCEMENT
            elif message.properties['message_type'] == 'AgentCheckinAnnouncement':
                log("rabbitmq-consumer:_on_response", "Got AgentCheckinAnnouncement at {0}".format(message.timestamp))
                agentCheckin = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Publishing message: {0}".format(str(agentCheckin)))
                self.socketio.emit('agentCheckin', agentCheckin)

            # AGENT COMMANDS UPDATED
            elif message.properties['message_type'] == 'AgentCommandsUpdated':
                log("rabbitmq-consumer:_on_response", "Got AgentCommandsUpdated at {0}".format(message.timestamp))
                agentCommandsUpdated = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Publishing message: {0}".format(str(agentCommandsUpdated)))
                self.socketio.emit('agentCommandsUpdated', agentCommandsUpdated, room=agentCommandsUpdated["AgentId"])

            # AGENT UPDATED
            elif message.properties['message_type'] == 'AgentUpdated':
                log("rabbitmq-consumer:_on_response", "Got AgentUpdated at {0}".format(message.timestamp))
                agentUpdated = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Publishing message: {0}".format(str(agentUpdated)))
                self.socketio.emit('agentUpdated', agentUpdated)

            # CONSOLE MESSAGE ANNOUNCEMENT
            elif message.properties['message_type'] == 'ConsoleMessageAnnouncement':
                log("rabbitmq-consumer:_on_response", "Got ConsoleMessageAnnouncement")
                message = json.loads(message.body)
                consoleMessage = message['ConsoleMessage']
                consoleMessage['Username'] = message['Username']
                consoleMessage.pop('Content', None)
                log("rabbitmq-consumer:_on_response", "Publishing message: {0}".format(str(consoleMessage)))
                self.socketio.emit('consoleMessageAnnouncement', consoleMessage, room=consoleMessage["AgentId"])

            # DEV PAYLOAD CREATED
            elif message.properties['message_type'] == 'DevPayloadCreated':
                log("rabbitmq-consumer:_on_response", "Got DevPayloadCreated at {0}".format(message.timestamp))
                devPayloadComplete = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Publishing message: {0}".format(str(devPayloadComplete)))
                self.socketio.emit('devPayloadCreated', devPayloadComplete)

            # ERROR MESSAGE ANNOUNCEMENT
            elif message.properties['message_type'] == 'ErrorMessageAnnouncement':
                log("rabbitmq-consumer:_on_response", "Got ErrorMessageAnnouncement at {0}".format(message.timestamp))
                errorMessageAnnouncement = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Publishing message: {0}".format(str(errorMessageAnnouncement)))
                # TL;DR - We only broadcast errors if they didn't come from API
                # I *think* this is the right way to go about this. API errors shouldn't typically be of interest to
                # everyone using Faction and the API is going to reply back with the error message when it encounters
                # it.
                if errorMessageAnnouncement['Source'] != 'API':
                    self.socketio.emit('errorMessageAnnouncement', errorMessageAnnouncement)
                else:
                    self.socketio.emit('errorMessageAnnouncement', errorMessageAnnouncement, broadcast=True)

            # NEW FACTION FILE
            elif message.properties['message_type'] == 'NewFactionFile':
                log("rabbitmq-consumer:_on_response", "Got NewFactionFile")
                fileMessage = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Emitting: {0}".format(message.body))
                self.socketio.emit('newFile', fileMessage)

            # NEW AGENT
            elif message.properties['message_type'] == 'NewAgent':
                log("rabbitmq-consumer:_on_response", "Got NewAgent at {0}".format(message.timestamp))
                agent = json.loads(message.body)
                agent['Success'] = True
                log("rabbitmq-consumer:_on_response", "Publishing message: {0}".format(str(agent)))
                self.socketio.emit('newAgent', agent, broadcast=True)

            # PAYLOAD CREATED
            elif message.properties['message_type'] == 'PayloadCreated':
                log("rabbitmq-consumer:_on_response", "Got PayloadCreated")
                payloadMessage = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Emitting: {0}".format(message.body))
                self.socketio.emit('payloadCreated', payloadMessage)

            # PAYLOAD UPDATED
            elif message.properties['message_type'] == 'PayloadUpdated':
                log("rabbitmq-consumer:_on_response", "Got PayloadUpdate")
                payloadUpdateMessage = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Emitting: {0}".format(message.body))
                self.socketio.emit('payloadUpdated', payloadUpdateMessage)

            # TRANSPORT CREATED
            elif message.properties['message_type'] == 'TransportCreated':
                log("rabbitmq-consumer:_on_response", "Got TransportCreated")
                transportMessage = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Emitting: {0}".format(message.body))
                self.socketio.emit('transportCreated', transportMessage)

            # TRANSPORT UPDATED
            elif message.properties['message_type'] == 'TransportUpdated':
                log("rabbitmq-consumer:_on_response", "Got TransportUpdated")
                transportMessage = json.loads(message.body)
                log("rabbitmq-consumer:_on_response", "Emitting: {0}".format(message.body))
                self.socketio.emit('transportUpdated', transportMessage)

            # AGENT CHECKIN ANNOUNCEMENT
            # TODO: Why aren't we doing anything with this?
            elif message.properties['message_type'] == 'AgentCheckinAnnouncement':
                log("rabbitmq-consumer:_on_response", "Got AgentCheckinAnnouncement!")

            # AGENT TASKUPDATE
            # TODO: Why aren't we doing anything with this?
            elif message.properties['message_type'] == 'AgentTaskUpdate':
                log("rabbitmq-consumer:_on_response", "Got AgentTaskUpdate")
        except Exception as e:
            log("rabbitmq-consumer:_on_response", "ERROR PROCESSING RABBITMQ MESSAGE: {0}".format(e))


rabbit_consumer = Consumer()


class Producer(object):
    """Asynchronous Rpc client."""

    def __init__(self):
        log("rabbitmq-producer:open", "Creating client..")
        self.queue = {}
        self.host = RABBIT_HOST
        self.username = RABBIT_USERNAME
        self.password = RABBIT_PASSWORD
        self.channel = None
        self.connection = None
        self.rpc_queue = 'ApiService'
        self.callback_queue = None
        self.open()

    def open(self):
        """Open Connection."""
        rabbit_connected = False
        log("rabbitmq-producer:open", "Opening Connection..")
        log("rabbitmq-producer:open", "Checking RabbitMQ..")
        while not rabbit_connected:
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
                                                                               credentials=credentials,
                                                                               socket_timeout=2,
                                                                               blocked_connection_timeout=2))
                rabbit_connected = True
                log("rabbitmq-producer:open", "RabbitMQ is up!")
                connection.close()
            except:
                rabbit_connected = False
                log("rabbitmq-producer:open", "RabbitMQ not reachable.. waiting..")
                sleep(2)
        return self

    def send_request(self, routing_key, message, callback=False):
        # Create the Message object.
        log("rabbitmq-producer:send_request", "Got message: {0} with routing_key: {1}".format(message, routing_key))

        message = Message.create(rabbit_consumer.channel, json.dumps(message))
        if callback:
            message.reply_to = rabbit_consumer.callback_queue
            rabbit_consumer.update_queue(message.correlation_id)
        # Create an entry in our local dictionary, using the automatically
        # generated correlation_id as our key.

        message.properties['message_type'] = routing_key

        # Publish the RPC request.
        log("rabbitmq-producer:send_request", "Publishing message..")
        message.publish(routing_key=routing_key, exchange='Core')

        # Return the Unique ID used to identify the request.

        log("rabbitmq-producer:send_request", "Got correlation_id: {0}".format(str(message.correlation_id)))
        return message.correlation_id


rabbit_producer = Producer()
