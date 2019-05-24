from flask import jsonify
from flask_restful import Resource, fields, reqparse
from flask_login import current_user, login_required
from processing import user, user_role
from processing.user_role import authorized_groups
from processing.api_key import new_api_key

user_parser = reqparse.RequestParser()
user_parser.add_argument('Username')
user_parser.add_argument('Password')
user_parser.add_argument('RoleName')
user_parser.add_argument('Enabled')
user_parser.add_argument('Visible')

api_key_parser = reqparse.RequestParser()
api_key_parser.add_argument('AccessKeyId')
api_key_parser.add_argument('AccessSecret')

change_password_parser = reqparse.RequestParser()
change_password_parser.add_argument('CurrentPassword')
change_password_parser.add_argument('NewPassword')


class LoginEndpoint(Resource):
    # Login has no permissions since we aren't logged in.
    def get(self):
        if current_user.is_authenticated:
            return jsonify({
                'Success': True,
                'Message': 'User is logged in'
            })
        else:
            return jsonify({
                'Success': False,
                'Message': 'User is not logged in'
            })

    def post(self):
        args = user_parser.parse_args()
        print('GOT ARGS: %s' % args)
        return jsonify(user.login_faction_user(args['Username'], args['Password']))


class LogoutEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self):
        if current_user.is_authenticated:
            user.logout_faction_user(current_user)
            return jsonify({
                'Success': True,
                'Message': 'Successfully Logged Out'
            })
        else:
            return jsonify({
                'Success': False,
                'Message': 'Invalid Request'
            }, 400)


class ChangePasswordEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def post(self, user_id=None):
        log("ChangePasswordEndpoint", "Got request from user: {0}".format(user_id))
        args = change_password_parser.parse_args()
        return jsonify(current_user.change_password(args['CurrentPassword'], args['NewPassword']))

    @authorized_groups(["Admin"])
    def patch(self, user_id):
        args = change_password_parser.parse_args()
        return jsonify(user.update_password(user_id, args['NewPassword']))



class ApiKeyEndpoint(Resource):
    @authorized_groups(['StandardRead'])
    def get(self, user_id):
        if current_user.Id == user_id:
            return jsonify(current_user.get_api_keys())
        else:
            return jsonify({
                'Success': False,
                'Message': "Not authorized."
            }, 400)

    @authorized_groups(['StandardRead'])
    def post(self, user_id):
        if current_user.Id == user_id:
            return jsonify(new_api_key("Access", user_id))
        else:
            return jsonify({
                'Success': False,
                'Message': "Not authorized."
            }, 400)

    @authorized_groups(['StandardRead'])
    def delete(self, user_id, api_key_id):
        if current_user.Id == user_id:
            return jsonify(current_user.delete_api_key(api_key_id))
        else:
            return jsonify({
                'Success': False,
                'Message': "Not authorized."
            }, 400)


class UserEndpoint(Resource):
    @authorized_groups(["Admin"])
    def get(self, user_id='all'):
        return jsonify(user.get_user(user_id))

    @authorized_groups(["Admin"])
    def post(self):
        args = user_parser.parse_args()
        log("UserEndpoint:Post", "got args: {0}".format(args))
        return jsonify(user.create_user(args['Username'], args['Password'], args['RoleName']))

    @authorized_groups(["Admin"])
    def put(self, user_id):
        args = user_parser.parse_args()
        response = user.update_user(user_id,
                                    username=args.get('Username'),
                                    role_id=args.get('RoleId'),
                                    enabled=args.get('Enabled'),
                                    visible=args.get('Visible'))
        return jsonify(response)

    @authorized_groups(["Admin"])
    def delete(self, user_id):
        return jsonify(user.update_user(user_id, enabled=False, visible=False))

class UserRoleEndpoint(Resource):
    @authorized_groups(["Admin"])
    def get(self, user_role_id='all'):
        return jsonify(user_role.get_role(user_role_id))