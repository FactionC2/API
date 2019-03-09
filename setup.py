
import secrets
import bcrypt
from datetime import datetime

from models.api_key import ApiKey
from models.user import User
from models.transport import Transport

from processing.user import create_user, update_user
from processing.user_role import create_role
from config import ADMIN_USERNAME, ADMIN_PASSWORD

from backend.database import db
from app import create_app

def setup():
    print("[setup] running..")
    app = create_app()
    with app.app_context():
        print("[setup] Creating Roles..")
        create_role("System")
        create_role("Admin")
        create_role("Operator")
        create_role("ReadOnly")


        print("[setup] Creating System user")
        user = User.query.get(1)
        if user:
            update_user(1)
        create_user("system", secrets.token_urlsafe(64), "system")

        print("[setup] Creating Admin user")
        user = User.query.get(2)
        if user:
            update_user(2)
        create_user(ADMIN_USERNAME, ADMIN_PASSWORD, "admin")


        print("[setup] Creating ApiKey for DIRECT Transport")
        apiKey = ApiKey()
        apiKey.Type = 'Transport'

        name = secrets.token_urlsafe(12)
        token = secrets.token_urlsafe(48)
        apiKey.Name = name
        apiKey.Key = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt())
        apiKey.Created = datetime.utcnow()
        apiKey.UserId = 1
        apiKey.OwnerId = 1
        apiKey.Enabled = True
        apiKey.Visible = True
        db.session.add(apiKey)
        db.session.commit()

        print("[setup] Creating DIRECT Transport..")
        transport = Transport()
        transport.Name = 'DIRECT'
        transport.Description = 'DIRECT Transport'
        transport.Guid = '0000-0000-0000-0000-0000'
        transport.ApiKeyId = apiKey.Id
        transport.Configuration = '[{"Name":"URL", "Value":"http://172.16.70.132:5000"},{"Name":"KEYNAME", "Value":"' + apiKey.Name + '"},{"Name":"SECRET","Value":"' + token +'"}]'
        transport.Created = datetime.utcnow()
        transport.Enabled = False
        transport.Visible = True
        db.session.add(transport)
        db.session.commit()

if __name__ == "__main__":
    print("[main] running setup()")
    setup()