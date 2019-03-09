import bcrypt
import secrets
from datetime import datetime

from backend.database import db
from models.api_key import ApiKey

def api_key_json(api_key):
    return {
        "Id": api_key.Id,
        "Name": api_key.Name,
        "OwnerId": api_key.OwnerId,
        "Type": api_key.Type,
        "Enabled": api_key.Enabled,
        "Visible": api_key.Visible
    }

def new_api_key(type, user_id, owner_id=None):
    api_key = ApiKey()
    api_key.UserId = user_id
    api_key.OwnerId = user_id

    # Owner ID is used when an api key is created for another account, for example when a user creates a new transport
    # the api key for the transport is created under the system user (who has no privs)
    if owner_id:
        api_key.OwnerId = owner_id
    api_key.Type = type

    token = secrets.token_urlsafe(48)
    api_key.Name = secrets.token_urlsafe(12)
    api_key.Key = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt())
    api_key.Enabled = True
    api_key.Visible = True
    api_key.Created = datetime.utcnow()

    db.session.add(api_key)
    db.session.commit()
    return {
        'Success': True,
        'Id': api_key.Id,
        'Name': api_key.Name,
        'Secret': token
    }


def get_api_key(api_key_id='all'):
    keys = []
    results = []
    if api_key_id == 'all':
        keys = ApiKey.query.all()
    else:
        keys.append(ApiKey.query.get(api_key_id))

    for key in keys:
        results.append(api_key_json(key))

    return {
        'Success': True,
        'Results': results
    }

def get_api_key_name(api_key_id):
    key = ApiKey.query.get(api_key_id)
    return key.Name