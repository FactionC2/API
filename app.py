import os
import secrets
import psycopg2
from time import sleep

from flask import Flask, send_from_directory
from flask_restful import Api
from flask_cors import CORS
import eventlet
import pika

from config import SECRET_KEY, DB_URI, RABBIT_URL, UPLOAD_DIR
from backend.database import db
from backend.cache import cache

eventlet.monkey_patch()
from models.user import login_manager, ApiSessionInterface

from apis.rest.agent import AgentEndpoint
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

from apis.socketio import socketio

# Setting this to true weakens CORS. DO NOT LEAVE THIS SET TO TRUE IN PROD
dev = True


def create_app():
    print("[app.py:CreateApp] - Started..")
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    # Even though we don't set a remember_me cookie, if anyone figured out how to create one it'd be bad news. We need
    # to make sure we won't accept a remember me cookie, so we set the name of the cookie we're looking for to
    # something random at startup. Probably a better way to do this, but this works for now.
    app.config['REMEMBER_COOKIE_NAME'] = secrets.token_urlsafe(64)
    db.init_app(app)

    # Disable Session Cookies
    app.session_interface = ApiSessionInterface()

    api = Api(app, prefix='/api/v1')

    # Agent REST endpoints
    api.add_resource(AgentEndpoint, '/agent/','/agent/<int:agent_id>/')
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

    login_manager.init_app(app)
    socketio.init_app(app, host='0.0.0.0', manage_session=False, message_queue=RABBIT_URL, channel="ConsoleMessages")
    CORS(app, supports_credentials=dev)
    cache.init_app(app)
    print("[app.py:CreateApp] - Finished.")

    return app


app = create_app()
print("[app.py] app created, continuing..")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

if __name__ == '__main__':
    print("[app.py:main] main starting...")
    socketio.run(app, host='0.0.0.0', max_size=4192)
else:
    print("foo")
