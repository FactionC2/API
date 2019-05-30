import os
import secrets
from logger import log
import eventlet
eventlet.monkey_patch()

from apis.socketio import socketio


# Setting this to true weakens CORS. DO NOT LEAVE THIS SET TO TRUE IN PROD
dev = True

log("app.py:main", "Started..")


def create_app():
    from flask import Flask
    from config import SECRET_KEY, DB_URI, RABBIT_URL, UPLOAD_DIR
    log("app.py:CreateApp", "Started..")
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['USE_RELOADER'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    # Even though we don't set a remember_me cookie, if anyone figured out how to create one it'd be bad news. We need
    # to make sure we won't accept a remember me cookie, so we set the name of the cookie we're looking for to
    # something random at startup. Probably a better way to do this, but this works for now.
    app.config['REMEMBER_COOKIE_NAME'] = secrets.token_urlsafe(64)

    log("app.py:CreateApp", "Initializing DB..")
    from backend.database import db
    db.init_app(app)

    log("app.py:CreateApp", "Creating API..")
    from flask_restful import Api
    api = Api(prefix='/api/v1')

    # REST imports
    log("app.py:CreateApp", "01")
    from apis.rest.agent import AgentEndpoint
    log("app.py:CreateApp", "02")
    from apis.rest.agent_checkin import AgentCheckinEndpoint
    log("app.py:CreateApp", "03")
    from apis.rest.agent_task import AgentTaskEndpoint
    log("app.py:CreateApp", "04")
    from apis.rest.agent_type import AgentTypeEndpoint
    log("app.py:CreateApp", "05")
    from apis.rest.console import ConsoleAgentEndpoint, ConsoleTaskEndpoint
    log("app.py:CreateApp", "06")
    from apis.rest.error_message import ErrorMessageEndpoint
    log("app.py:CreateApp", "07")
    from apis.rest.faction_file import FactionFileEndpoint, FactionFileDownloadEndpoint, FactionFileBytesEndpoint
    log("app.py:CreateApp", "08")
    from apis.rest.ioc import IOCEndpoint
    log("app.py:CreateApp", "09")
    from apis.rest.payload import PayloadEndpoint, PayloadFileEndpoint
    log("app.py:CreateApp", "10")
    from apis.rest.staging import StagingEndpoint
    log("app.py:CreateApp", "11")
    from apis.rest.transport import TransportEndpoint
    log("app.py:CreateApp", "12")
    from apis.rest.user import LoginEndpoint, ChangePasswordEndpoint, ApiKeyEndpoint, UserEndpoint, \
        UserRoleEndpoint

    # Agent REST endpoints
    log("app.py:CreateApp", "Registering Endpoints..")
    api.add_resource(AgentEndpoint, '/agent/', '/agent/<int:agent_id>/')
    api.add_resource(AgentCheckinEndpoint, '/agent/<string:agent_name>/checkin/')
    api.add_resource(AgentTypeEndpoint, '/agent/type/', '/agent/type/<int:agent_type_id>/')
    api.add_resource(ConsoleAgentEndpoint, '/agent/<int:agent_id>/console/')

    # User REST endpoints
    api.add_resource(LoginEndpoint, '/login/')
    api.add_resource(UserEndpoint, '/user/', '/user/<int:user_id>/')
    api.add_resource(ChangePasswordEndpoint, '/user/<int:user_id>/password/')
    api.add_resource(ApiKeyEndpoint, '/user/<int:user_id>/apikeys/', '/user/<int:user_id>/apikeys/<int:api_key_id>/')
    api.add_resource(UserRoleEndpoint, '/user/role/', '/user/role/<int:user_role_id>/')

    # Task REST endpoints
    api.add_resource(AgentTaskEndpoint, '/task/', '/task/<int:agent_task_id>/')
    api.add_resource(ConsoleTaskEndpoint, '/task/<int:agent_task_id>/console/')

    # Faction FIle Endpoint
    api.add_resource(FactionFileEndpoint, '/file/', '/file/<string:faction_file_name>')
    api.add_resource(FactionFileDownloadEndpoint, '/file/<string:faction_file_name>/download/')
    api.add_resource(FactionFileBytesEndpoint, '/file/<string:faction_file_name>/bytes/')

    # Misc REST endpoints
    api.add_resource(ErrorMessageEndpoint, '/errors/', '/errors/<int:error_message_id>')
    api.add_resource(IOCEndpoint, '/ioc/', '/ioc/<int:ioc_id>/')
    api.add_resource(PayloadEndpoint, '/payload/', '/payload/<int:staging_config_id>/')
    api.add_resource(PayloadFileEndpoint, '/payload/<int:payload_id>/file/')
    api.add_resource(StagingEndpoint, '/staging/', '/staging/<string:payload_name>/<string:staging_id>/')
    api.add_resource(TransportEndpoint, '/transport/', '/transport/<int:transport_id>/')

    api.init_app(app)

    log("app.py:CreateApp", "Setting up CORS..")
    from flask_cors import CORS
    CORS(app, supports_credentials=dev)

    log("app.py:CreateApp", "Setting up Cache..")
    from backend.cache import cache
    cache.init_app(app)

    log("app.py:CreateApp", "Setting up Login Manager..")
    from models.user import login_manager, ApiSessionInterface
    login_manager.init_app(app)

    # Disable Session Cookies
    log("app.py:CreateApp", "Updating Session Interface..")
    app.session_interface = ApiSessionInterface()

    log("app.py:CreateApp", "Setting up socketio..")
    socketio.init_app(app, host='0.0.0.0', manage_session=False, message_queue=RABBIT_URL, channel="ConsoleMessages")

    from backend.rabbitmq import rabbit_consumer
    rabbit_consumer.socketio = socketio
    socketio.start_background_task(target=rabbit_consumer.process_data_events)

    # Check Upload Dir
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    log("app.py:CreateApp", "Finished.")
    return app


if __name__ == '__main__':
    log("app.py:main", "main starting...")
    socketio.run(create_app())
# else:
#     app = create_app()
