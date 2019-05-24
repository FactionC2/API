import base64
import bcrypt
import pickle
from datetime import datetime

from flask import g
from flask.sessions import SecureCookieSessionInterface
from flask_login import user_loaded_from_header, user_loaded_from_request

from logger import log
from backend.database import db
from backend.cache import cache
from flask import jsonify
from flask_login import LoginManager
from models.api_key import ApiKey
from models.console_message import ConsoleMessage

login_manager = LoginManager()


class User(db.Model):
    __tablename__ = "User"
    Id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String, unique=True)
    Password = db.Column(db.LargeBinary)
    RoleId = db.Column(db.Integer, db.ForeignKey('UserRole.Id'), nullable=False)
    ApiKeys = db.relationship("ApiKey", backref='User', lazy=True)
    Authenticated = db.Column(db.Boolean, default=False)
    ConsoleMessages = db.relationship("ConsoleMessage", backref='User', lazy=True)
    Files = db.relationship("FactionFile", backref='User', lazy=True)
    Created = db.Column(db.DateTime)
    LastLogin = db.Column(db.DateTime)
    Enabled = db.Column(db.Boolean)
    Visible = db.Column(db.Boolean)


    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.Username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.Authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def change_password(self, current_password, new_password):
        log("change_password", "Got password change request")
        if bcrypt.checkpw(current_password.encode('utf-8'), self.Password) and self.Enabled:
            self.Password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            db.session.add(self)
            db.session.commit()
            log("change_password", "Password changed")
            return dict({
                "Success": True,
                "Message": 'Changed password for user: {0}'.format(self.Username)
            })
        log("change_password", "Current password incorrect")
        return {
            'Success':False,
            'Message':'Invalid username or password.'
        }

    def get_api_keys(self):
        api_keys = self.ApiKeys
        log("get_api_keys", "Got api keys: {0}".format(str(api_keys)))
        results = []
        for api_key in api_keys:
            result = dict()
            result['Id'] = api_key.Id
            result['Name'] = api_key.Name
            result['Created'] = None
            result['LastUsed'] = None
            result['Type'] = api_key.Type
            if api_key.Created:
                result['Created'] = api_key.Created.isoformat()
            if api_key.LastUsed:
                result['LastUsed'] = api_key.LastUsed.isoformat()
            results.append(result)
        return {
            'Success':True,
            'Results':results
        }

    def delete_api_key(self, api_key_id):
        api_keys = self.ApiKeys
        for api_key in api_keys:
            if api_key.Id == api_key_id:
                db.session.delete(api_key)
                db.session.commit()
                return {
                    'Success':True,
                    'Message':"Api Key {0} deleted".format(api_key.Name)
                }
        return {
            'Success':False,
            'Message':"Api Key ID: {0} not found".format(api_key_id)
            }

class ApiSessionInterface(SecureCookieSessionInterface):
    # Taken from https://flask-login.readthedocs.io/en/latest/#disabling-session-cookie-for-apis
    # I'm believe this is the proper way to do this since we're an API and don't care about
    # session cookies.

    def open_session(self, app, request):
        s = self.get_signing_serializer(app)
        if s is None:
            return None
        else:
            return self.session_class()

    def should_set_cookie(self, app, session):
        return False

    def save_session(self, *args, **kwargs):
        log("user model", "save session called")
        return

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    log("user_loader", "Called for user_id: {0}".format(user_id))
    """Load user by ID from cache, if not in cache, then cache it."""
    # make a unique cache key for each user
    user_key = 'user_{}'.format(user_id)
    # check if the user_object is cached
    user_obj = pickle.loads(cache.get(user_key)) if cache.get(user_key) else None
    if user_obj:
        return user_obj
    elif isinstance(user_id, int):
        user = User.query.get(user_id)
        user_obj = pickle.dumps(user)
        cache.set(user_key, user_obj, timeout=3600)
        return user
    else:
        user = User.query.filter_by(Username = user_id).first()
        user_obj = pickle.dumps(user)
        cache.set(user_key, user_obj, timeout=3600)
        return user

@user_loaded_from_header.connect
def user_loaded_from_header(self, user=None):
    log("user model", "User loaded from header")
    g.login_via_header = True

@user_loaded_from_request.connect
def user_loaded_from_request(self, user=None):
    log("user model", "User loaded from request")
    g.login_via_request = True

@login_manager.request_loader
def load_user_from_request(request):
    # next, try to login using Basic Auth
    print('Trying API key lookup')
    keyid = None
    secret = None

    try:
        keyid = request.cookies['AccessKeyId']
        secret = request.cookies['AccessSecret']
    except:
        pass
    try:
        auth_header = request.headers.get('Authorization')
        auth_type, credentials = auth_header.split(' ')
        decoded_header = base64.b64decode(credentials).decode("utf-8")
        keyid, secret = decoded_header.split(':')
    except:
        pass
    try:
        token = request.args.get('token')
        keyid, secret = token.split(':')
    except:
        pass
    if secret and keyid:
        print('Got API KEY: {0}'.format(keyid))
        apiKey = ApiKey.query.filter_by(Name=keyid).first()
        if apiKey and apiKey.Enabled:
            if bcrypt.checkpw(secret.encode('utf-8'), apiKey.Key):
                print('Returning User with Id: {0}'.format(str(apiKey.UserId)))
                apiKey.LastUsed = datetime.utcnow()
                db.session.add(apiKey)

                user = User.query.get(apiKey.UserId)
                user.LastLogin = datetime.utcnow()
                db.session.add(user)
                db.session.commit()
                return user
        db.session.remove()
    else:
        print('Invalid API Key or Secret')
        db.session.remove()
    # finally, return None if both methods did not login the user
    db.session.remove()
    return None

