import flask, flask_cors
from flask_socketio import SocketIO, join_room, leave_room
import logging

from hanabi_api.api import game
from hanabi_api.api.piece import Pieces
from hanabi_api.api.player import Players
from hanabi_api.utils.database import Database

LOGGER = logging.getLogger(__name__)
app = flask.Flask(__name__)
flask_cors.CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')
database = Database()

app.add_url_rule(rule='/game', view_func=game.Games.as_view('game'), methods=['GET', 'POST'])
app.add_url_rule(rule='/player/<player_id>', view_func=Players.as_view('player'))
app.add_url_rule(rule='/piece/<piece_id>', view_func=Pieces.as_view('piece'), methods=['GET', 'POST'])