#!/usr/bin/env python3

import os
import sys
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
    from apis.rest.agent import AgentEndpoint
    from apis.rest.agent_commands import AgentCommandEndpoint
    from apis.rest.agent_checkin import AgentCheckinEndpoint
    from apis.rest.agent_task import AgentTaskEndpoint
    from apis.rest.agent_type import AgentTypeEndpoint
    from apis.rest.console import ConsoleAgentEndpoint, ConsoleTaskEndpoint
    from apis.rest.error_message import ErrorMessageEndpoint
    from apis.rest.faction_file import FactionFileEndpoint, FactionFileDownloadEndpoint, FactionFileBytesEndpoint
    from apis.rest.ioc import IOCEndpoint
    from apis.rest.payload import PayloadEndpoint, PayloadFileEndpoint
    from apis.rest.staging import StagingEndpoint
    from apis.rest.transport import TransportEndpoint
    from apis.rest.user import LoginEndpoint, ChangePasswordEndpoint, ApiKeyEndpoint, UserEndpoint, \
        UserRoleEndpoint

    # Agent REST endpoints
    log("app.py:CreateApp", "Registering Endpoints..")
    api.add_resource(AgentEndpoint, '/agent/', '/agent/<int:agent_id>/')
    api.add_resource(AgentCheckinEndpoint, '/agent/<string:agent_name>/checkin/')
    api.add_resource(AgentTypeEndpoint, '/agent/type/', '/agent/type/<int:agent_type_id>/')
    api.add_resource(ConsoleAgentEndpoint, '/agent/<int:agent_id>/console/')
    api.add_resource(AgentCommandEndpoint, '/agent/<int:agent_id>/commands/')

    # User REST endpoints
    api.add_resource(LoginEndpoint, '/login/')
    api.add_resource(UserEndpoint, '/user/', '/user/<int:user_id>/')
    api.add_resource(ChangePasswordEndpoint, '/user/<int:user_id>/password/')
    api.add_resource(ApiKeyEndpoint, '/user/<int:user_id>/apikey/', '/user/<int:user_id>/apikey/<int:api_key_id>/')
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
    # startup.sh will default to 0.0.0.0 for docker containers
    host = os.environ.get("GUNICORN_BIND_ADDRESS", "127.0.0.1")
    port = int(os.environ.get("GUNICORN_BIND_PORT", 5000))
    # You can add extra logging around socketio by setting the following options here: logger=True, engineio_logger=True
    socketio.init_app(app, host=host, port=port, async_mode='eventlet', manage_session=False, message_queue=RABBIT_URL, channel="ConsoleMessages",
                      cors_allowed_origins="*")

    from backend.rabbitmq import rabbit_consumer
    rabbit_consumer.socketio = socketio
    socketio.start_background_task(target=rabbit_consumer.process_data_events)

    # Check Upload Dir
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    log("app.py:CreateApp", "Finished.")
    return app


app = create_app()

if __name__ == '__main__':
    log("app.py:main", "main starting...")
    host = os.environ.get("GUNICORN_BIND_ADDRESS", "127.0.0.1")
    port = int(os.environ.get("GUNICORN_BIND_PORT", 5000))
    is_debug = int(os.environ.get("GUNICORN_DEBUG", 0)) == 1
    is_reloading = int(os.environ.get("GUNICORN_RELOAD", 0)) == 1
    log("app.py:main", f"Binding on {str(host)}:{str(port)}")
    log("app.py:main", f"SocketIO Mode is {str(socketio.server.eio.async_mode)}")
    if is_debug:
        log("app.py:main", "Debug Mode Enabled")
    if is_reloading:
        log("app.py:main", "Reloading Enabled")

    socketio.run(
        app, 
        host=host, 
        port=port, 
        debug=is_debug, 
        use_reloader=is_reloading, 
        log_output=True
    )
