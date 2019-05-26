from datetime import datetime, timedelta

from flask_login import login_user, logout_user, current_user
from sqlalchemy import func
import bcrypt

from backend.database import db
from backend.cache import cache

from models.user import User
from models.api_key import ApiKey

from processing.user_role import get_role_id, get_role_name
from processing.api_key import new_api_key

from logger import log


def user_json(user):
    log("user_json", "Working on user: {0}".format(user))
    lastLogin = None
    if user.LastLogin:
        lastLogin = user.LastLogin.isoformat()
    result = {
        'Id': user.Id,
        'Username': user.Username,
        'Role': get_role_name(user.RoleId),
        'LastLogin': lastLogin,
        'Created': user.Created.isoformat(),
        'Authenticated': user.Authenticated,
        'Enabled': user.Enabled,
        'Visible': user.Visible
    }
    log("user_json", "returning: {0}".format(result))
    return result


def login_faction_user(username, password):
    log("login_faction_user", "Checking " + username)
    user = User.query.filter(func.lower(User.Username) == func.lower(username)).first()
    print(user)

    if user:
        log("login_faction_user", "Got user: " + user.Username)
        if bcrypt.checkpw(password.encode('utf-8'), user.Password) and user.Enabled:
            log("login_faction_user", "Login successful")
            # System user is treated a little special
            if user.Username.lower() == 'system' or user.Id == 1:
                expiration_time = datetime.utcnow() - timedelta(minutes=5)
                api_key_type = 'FileUpload'
                ApiKey.query.filter(ApiKey.UserId == user.Id)\
                    .filter(ApiKey.Type == api_key_type)\
                    .filter(ApiKey.Created < expiration_time) .delete()
            else:
                user.Authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user)
                api_key_type = 'SessionToken'
                # User has logged in with a username and password. Clear their SessionToken and create a new one.
                ApiKey.query.filter(ApiKey.UserId == user.Id).filter(ApiKey.Type == api_key_type).delete()

            token = new_api_key(api_key_type, user.Id)

            return dict({
                "Success": True,
                "UserId": user.Id,
                "Username": user.Username,
                "UserRole": get_role_name(user.RoleId),
                "AccessKeyId": token['Name'],
                "AccessSecret": token['Secret']
            })
    log("login_faction_user", "Username or password no good")
    return dict({
        "Success": False,
        "Message": 'Invalid Username or Password'
    })


def logout_faction_user(user_id):
    user = User.query.get(user_id)
    user.Authenticated = False
    db.session.add(user)
    db.session.commit()
    ApiKey.query.filter(ApiKey.UserId == user.Id).filter(ApiKey.Type == 'SessionToken').delete()
    user = 'user_{}'.format(current_user.Id)
    cache.delete(user)
    logout_user()
    return dict({
        "Success": True,
        "Message": "User has logged out"
    })


def get_user(user_id='all', include_hidden=False):
    users = []
    results = []
    if user_id == 'all':
        log("get_user", "Getting all users")
        if include_hidden:
            users = User.query.all()
        else:
            users = User.query.filter_by(Visible=True)
    else:
        log("get_user", "Getting user {0}".format(user_id))
        users.append(User.query.get(user_id))
    if users:
        for user in users:
            if user.Username.lower() != 'system':
                results.append(user_json(user))
        return dict({
            "Success": True,
            "Results": results
        })
    else:
        return dict({
            "Success": False,
            "Message": "User with ID {0} not found.".format(user_id)
        })

def create_user(username, password, role_name):
    user = User()
    user.Username = username
    user.Password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user.Created = datetime.utcnow()
    user.RoleId = get_role_id(role_name)
    user.Enabled = True
    user.Visible = True
    print(user.RoleId)
    print('Creating user %s ' % user.Username)
    db.session.add(user)
    db.session.commit()
    return dict({
        "Success": True,
        "Message": 'User {0} created successfully'.format(user.Username)
    })


def update_user(user_id, username=None, role_id=None, enabled=None, visible=None):
    if user_id < 3:
        return dict({
            "Success": False,
            "Message": 'Can not change the admin or system user'
        })
    user = User.query.get(user_id)

    if username is not None:
        user.username = username

    if role_id is not None:
        user.RoleId = role_id

    if enabled is not None:
        user.Enabled = enabled

    if visible is not None:
        user.Visible = visible

    db.session.add(user)
    db.session.commit()
    return dict({"Success": True, "Result": user_json(user)})


# This is called when an admin changes a users password
def update_password(user_id, new_password):
    user = User.query.get(user_id)
    if user:
        log("update_password", "Got user: " + user.Username)
        user.Password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        db.session.add(user)
        db.session.commit()
        return dict({
            "Success": True,
            "Message": 'Changed password for user: {0}'.format(user.Username)
        })
    return dict({
        "Success": False,
        "Message": 'Invalid User Id.'
    })
