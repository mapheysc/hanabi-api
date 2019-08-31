from pymongo import MongoClient
from pymongo import MongoClient
import flask, flask_cors
from flask_restful import Resource, Api
from flask_socketio import SocketIO, join_room, leave_room
import logging

from api.game import Games, MetaGames
from api.piece import Pieces
from api.player import Players
from api.user import Users

LOGGER = logging.getLogger(__name__)
app = flask.Flask(__name__)
flask_cors.CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')
client = MongoClient('mongodb://mongo:27017/')
database = client

api = Api(app)

api.add_resource(Games, '/game', '/game/<game_id>', endpoint='game')
api.add_resource(MetaGames, '/meta/game', '/meta/game/<meta_game_id>', endpoint='metagames')
api.add_resource(Players, '/player/<player_id>', endpoint='player')
api.add_resource(Pieces, '/piece/<piece_id>', endpoint='piece')
api.add_resource(Users, '/user', '/user/<user_id>', endpoint='user')