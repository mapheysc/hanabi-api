"""Route definitions for the Hanabi API."""

import flask_cors
import flask
import datetime
from flask_restful import Api
from flask_socketio import SocketIO
import logging
from flask_jwt_extended import JWTManager

from api.game import Games, MetaGames
from api.authenticate import Authenticate
from api.piece import Pieces
from api.player import Players
from api.user import Users
from api.config.config import Config
from utils.database import Database

LOGGER = logging.getLogger(__name__)
CONFIG = Config()
app = flask.Flask(__name__)
flask_cors.CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')
LOGGER.critical(f'Here')
database = Database()
app.config['JWT_SECRET_KEY'] = CONFIG['flask']['secret']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(
    hours=CONFIG['flask']['JWT_ACCESS_TOKEN_EXPIRES_HOURS'])
jwt = JWTManager(app)

api = Api(app)

api.add_resource(Authenticate, '/authenticate', endpoint='authenticate')
api.add_resource(Games, '/game', '/game/<game_id>', endpoint='game')
api.add_resource(MetaGames, '/meta/game', '/meta/game/<meta_game_id>',
                 endpoint='metagames')
api.add_resource(Players, '/player/<player_id>', endpoint='player')
api.add_resource(Pieces, '/piece/<piece_id>', endpoint='piece')
api.add_resource(Users, '/user', '/user/<user_id>', endpoint='user')
