from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource # used for REST API building

from model.players import Player

# Change variable name and API name and prefix
player_api = Blueprint('player_api', __name__,
                   url_prefix='/api/players')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(player_api)

class PlayerAPI:        
    class _Create(Resource):
        def post(self):
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Avoid garbage in, error checking '''
            # validate name
            name = body.get('name')
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 210
            # validate uid
            uid = body.get('uid')
            if uid is None or len(uid) < 2:
                return {'message': f'User ID is missing, or is less than 2 characters'}, 210
            # look for password and dob
            password = body.get('password')
            tokens = body.get('tokens')

            ''' #1: Key code block, setup USER OBJECT '''
            uo = Player(name=name, 
                      uid=uid,
                      tokens=tokens,)
            
            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None:
                uo.set_password(password)            
            
            ''' #2: Key Code block to add user to database '''
            # create user in database
            player = uo.create()
            # success returns json of user
            if player:
                return jsonify(player.read())
            # failure returns error
            return {'message': f'Processed {name}, either a format error or User ID {uid} is duplicate'}, 210

    class _Read(Resource):
        def get(self):
            players = Player.query.all()    # read/extract all users from database
            json_ready = [player.read() for player in players]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps

    class _Update(Resource):
        def put(self):
            body = request.get_json() # get the body of the request
            userid = body.get('uid') # get the UID (Know what to reference)
            data = body.get('data')
            user = Player.query.get(userid) # get the user (using the uid in this case)
            user.update(data)
            return f"{user.read()} Updated"

    class _Delete(Resource):
        def delete(self):
            body = request.get_json()
            uid = body.get('uid')
            user = Player.query.get(uid)
            user.delete()
            return f"{user.read()} Has been deleted"

    class _Security(Resource):

        def post(self):
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Get Data '''
            uid = body.get('uid')
            if uid is None or len(uid) < 2:
                return {'message': f'User ID is missing, or is less than 2 characters'}, 400
            password = body.get('password')
            
            ''' Find user '''
            user = Player.query.filter_by(_uid=uid).first()
            if user is None or not user.is_password(password):
                return {'message': f"Invalid user id or password"}, 400
            
            ''' authenticated user '''
            return jsonify(user.read())

    # building RESTapi endpoint
    api.add_resource(_Create, '/create')
    api.add_resource(_Read, '/')
    api.add_resource(_Delete, '/delete')
    api.add_resource(_Update, '/update')
    api.add_resource(_Security, '/authenticate')