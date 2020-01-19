from backend.rabbitmq import rabbit_producer
from models.error_message import ErrorMessage


def error_message_json(error_message):
    return {
        "Id": error_message.Id,
        "Source": error_message.Source,
        "Message": error_message.Message,
        "Details": error_message.Details,
        "Timestamp": error_message.Timestamp.isoformat()
    }

def create_error_message(message, details=None):
    error_message = dict({
        'Success': False,
        'Source': 'API',
        'Message': message,
        'Details': details
    })
    rabbit_producer.send_request("NewErrorMessage", error_message)
    return error_message

def new_error_message(source, message):
    error_message = dict({
        "Source": source,
        "Message": message
    })
    rabbit_producer.send_request("NewErrorMessage", error_message)

    return dict({
        'Success': True,
        'ErrorMessage': error_message
    })


def get_error_message(error_message_id='all'):
    error_messages = []
    results = []
    if error_message_id == 'all':
        error_messages = ErrorMessage.query.all()
    else:
        error_messages.append(ErrorMessage.query.get(error_message_id))

    for error_message in error_messages:
        results.append(error_message_json(error_message))

    return {
        'Success': True,
        'Results': results
    }