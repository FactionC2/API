import os
import base64
import hashlib
from datetime import datetime

from flask import json, request, send_from_directory
from itsdangerous import URLSafeSerializer
from flask_login import current_user
from werkzeug.utils import secure_filename
from backend.database import db
from backend.rabbitmq import rabbit_producer

from config import UPLOAD_DIR


from models.agent import Agent
from models.user import User
from models.faction_file import FactionFile

from processing.error_message import create_error_message

files_upload_dir = os.path.join(UPLOAD_DIR, 'files/')

def faction_file_json(faction_file):
    log("agent_json", "Working on %s" % faction_file)

    last_downloaded = None

    if faction_file.LastDownloaded:
        last_downloaded = faction_file.LastDownloaded.isoformat()

    agent_name = None
    if faction_file.AgentId:
        agent_name = Agent.query.get(faction_file.AgentId).Name

    user = User.query.get(faction_file.UserId)

    result = {
        'Id': faction_file.Id,
        'Name': faction_file.Name,
        'Hash': faction_file.Hash,
        'AgentId': faction_file.AgentId,
        'AgentName': agent_name,
        'Username': user.Username,
        'Created': faction_file.Created.isoformat(),
        'LastDownloaded': last_downloaded,
        'Visible': faction_file.Visible
    }
    return result

# Taken from: https://stackoverflow.com/a/22058673
def hash_file(filepath):

    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()

def get_faction_file(faction_file_name='all'):
    log("get_faction_file", "got faction file " + str(faction_file_name))
    result = []
    if faction_file_name == 'all':
        files = FactionFile.query.all()
        for file in files:
            result.append(faction_file_json(file))
    else:
        file = FactionFile.query.filter_by(Name=faction_file_name).order_by(FactionFile.Id.desc()).first()
        result.append(faction_file_json(file))
    return dict({
        'Results': result,
        'Success': True
    })

def new_faction_file(filename, filecontent, user_id=None, agent_id=None, hash=None):
    log("new_faction_file", "working on {0}".format(filename))
    faction_file = FactionFile()
    faction_file.Created = datetime.utcnow()
    faction_file.Visible = True
    faction_file.UserId = current_user.Id

    if faction_file.UserId == None:
        faction_file.UserId = 1

    log("new_faction_file", "UserId: {0}".format(faction_file.UserId))
    if agent_id:
        log("new_faction_file", "got agent id {0}".format(agent_id))
        agent = Agent.query.get(agent_id)
        log("new_faction_file", "got agent {0}".format(agent.Name))
        faction_file.AgentId = agent.Id
        log("new_faction_file", "set faction_file agent id to {0}".format(faction_file.AgentId))
        filename = "{0}_{1}_{2}".format(agent.Name, datetime.utcnow().strftime('%Y%m%d%H%M%S'), filename)

    faction_file.Name = secure_filename(filename)

    log("new_faction_file", "filename set to: {0}".format(faction_file.Name))
    try:
        savePath = os.path.join(files_upload_dir, faction_file.Name)
        log("new_faction_file:upload_faction_file", "saving file to: {0}".format(savePath))
        if hasattr(filecontent, 'save'):
            filecontent.save(savePath)
        else:
            file_bytes = base64.b64decode(filecontent)
            with open(savePath, 'wb') as f:
                f.write(file_bytes)

        faction_file.Hash = hash_file(savePath)

        if hash:
            if faction_file.Hash == hash:
                faction_file.HashMatch = True
            else:
                faction_file.HashMatch = False

        log("new_faction_file", "UserId: {0}".format(faction_file.UserId))
        db.session.add(faction_file)
        db.session.commit()
        message = dict({
            'Success': True,
            'Result': faction_file_json(faction_file)
        })
        rabbit_producer.socketio.emit('newFile', message)
        return faction_file
    except Exception as e:
        error_message = str(e)
        return create_error_message("Error creating file: {0}".format(error_message))

# PAYLOAD FILE STUFF #
def upload_faction_file(agent_name=None, hash=None, file_name=None, file_content=None):
    results = []
    error_message = None
    log("upload_faction_file", "called..")
    log("upload_faction_file", "Files in reqeust: {0}".format(request.files))
    log("upload_faction_file", "Agent Name: {0}".format(agent_name))
    log("upload_faction_file", "File Name: {0}".format(file_name))
    log("upload_faction_file", "File Content: {0}".format(file_content))

    files = request.files.getlist("files")
    log("upload_faction_file", "got files: {0}".format(files))
    if agent_name:
        agent_id = Agent.query.filter_by(Name=agent_name).first().Id
    else:
        agent_id = None

    if len(files) > 0:
        for file in files:
            faction_file = new_faction_file(file.filename, file, current_user.Id, agent_id, hash)
            results.append(faction_file_json(faction_file))
    elif file_content != None:
        faction_file = new_faction_file(file_name, file_content, current_user.Id, agent_id, hash)
        results.append(faction_file_json(faction_file))
    else:
        return dict({
            'Success': False,
            'Message': 'No files uploaded'
        })

    return dict({
        'Success': True,
        'Results': results
        })


def download_faction_file(faction_file_name):
    faction_file = FactionFile.query.filter_by(Name=faction_file_name).order_by(FactionFile.Id.desc()).first()
    print("UploadDir {0}".format(UPLOAD_DIR))
    print("FileUploadDir {0}".format(files_upload_dir))
    log("faction_file:download_faction_file", "upload path: {0}".format(files_upload_dir))
    if faction_file.Name:
        path = os.path.join(files_upload_dir, faction_file.Name)
        log("faction_file:download_faction_file", "returning path: {0}".format(path))
        faction_file.LastDownloaded = datetime.utcnow()
        db.session.add(faction_file)
        db.session.commit()

        return dict({
            'Success': True,
            'Message': path,
            'Filename': faction_file.Name
        })
    else:
        return dict({
            'Success': False,
            'Message': 'File does not exist'
        })


def get_faction_file_bytes(faction_file_name):
    faction_file = FactionFile.query.filter_by(Name=faction_file_name).first()
    if faction_file:
        path = os.path.join(files_upload_dir, faction_file.Name)
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        print(encoded)
        return dict({
            'Success': True,
            'Message': encoded
        })
    else:
        return dict({
            'Success': False,
            'Message': 'File does not exist'
        })
