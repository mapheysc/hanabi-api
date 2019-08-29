import flask, flask_cors
from flask_restful import Resource, Api
from flask_socketio import SocketIO, join_room, leave_room
import logging

from api.game import Games
from api.piece import Pieces
from api.player import Players
from utils.database import Database

LOGGER = logging.getLogger(__name__)
app = flask.Flask(__name__)
flask_cors.CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')
database = Database()

api = Api(app)

api.add_resource(Games, '/game', '/game/<game_id>', endpoint='game')
api.add_resource(Players, '/player/<player_id>', endpoint='player')
api.add_resource(Pieces, '/piece/<piece_id>', endpoint='piece')