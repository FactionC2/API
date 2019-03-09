import functools
from flask_login import current_user
from backend.database import db
from models.user_role import UserRole

standard_read = [
    'Admin',
    'Operator',
    'ReadOnly'
]

standard_write = [
    'Admin',
    'Operator'
]

# When one of these groups is specified, we substitute them for the 'system' group. This adds an extra check
# to make sure system api keys aren't used for anything weird. Its also the only way I could figure out how
# to make it work in the first place.
system_groups = [
    'Transport',
    'FileUpload'
]

# This function drives all of the authentication for the APIs
def authorized_groups(groups):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            print('[User Role - Authorized Groups] Checking if authenticated..')
            if not current_user.is_authenticated:
                print('Not authenticated.')
                return {
                    "Success": False,
                    "Message": "User is not authenticated"
                }, 401
            authorized = False

            # Replace meta group names with contents of meta group
            if 'StandardRead' in groups:
                groups.remove('StandardRead')
                groups.extend(standard_read)

            if 'StandardWrite' in groups:
                groups.remove('StandardWrite')
                groups.extend(standard_write)

            for system_group in system_groups:
                if system_group in groups:
                    groups.remove(system_group)
                    if 'system' not in groups:
                        groups.append('system')

            # Iterate through valid groups, checking if the user is in there.
            for group in groups:
                print("[User Role - Authorized Groups] checking group: {0}".format(group))
                group_id = get_role_id(group)
                print("[User Role - Authorized Groups] group id: {0}".format(group_id))
                if current_user.RoleId == group_id:
                    print('[User Role - Authorized Groups] Authorized.')
                    authorized = True

            if not authorized:
                print("[authorized_groups] User {0} is not in the following groups: {1}".format(current_user.Username, groups))
                return {
                    "Success":False,
                    "Message":"User does not have permissions to perform this action"
                }, 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

def role_json(role):
    return {
        'Id': role.Id,
        'Name': role.Name
    }

def create_role(name):
    role = UserRole()
    role.Name = name.lower()
    db.session.add(role)
    db.session.commit()

def get_role(role_id='all'):
    results = []
    print("[get_role] Getting role for id: {0}".format(role_id))
    if role_id == 'all':
        roles = UserRole.query.all()
    else:
        roles = UserRole.query.get(role_id)
    for role in roles:
        if role.Name.lower() != 'system':
            results.append(role_json(role))
    return dict({
        "Success": True,
        "Results": results
    })

def get_role_id(name):
    print("[get_role_id] Getting role {0}".format(name))
    role = UserRole.query.filter_by(Name=name.lower()).first()
    if role:
        print("[get_role_id] Got role {0}".format(role.Id))
        return role.Id
    else:
        print("[get_role_id] Role not found")
        return None

def get_role_name(role_id):
    print("[get_role_name] Getting role name {0}".format(role_id))
    role = UserRole.query.get(role_id)
    if role:
        print("[get_role_name] Got role name {0}".format(role.Name))
        return role.Name
    else:
        print("[get_role_name] Role not found")
        return None