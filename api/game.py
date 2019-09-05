"""Defines logic used for the endpoints found at ``/haiku``."""
import logging
import flask
import flask.views
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, jsonify, request, Response
from flask_restplus import abort
from bson.objectid import ObjectId

from hanabi.game import Game
from utils import socket
from api import rest
from utils.database import remove_object_ids_from_dict
LOGGER = logging.getLogger(__name__)


class Games(flask.views.MethodView):
    """Class containing REST methods for the ``/game`` endpoint."""

    @jwt_required
    def get(self, game_id=None):
        """REST endpoint that gets the current state of a game with a provided id."""
        LOGGER.info("Hitting REST endpoint: '/game'")

        if game_id is None:
            return jsonify([{
                'name': game['name'], 'id': str(game['_id'])
                } for game in rest.database.db.games.find()])
        else:
            game = rest.database.db.games.find_one({'_id': ObjectId(game_id)})
            if game is None:
                msg = 'Game cannot be found.'
                return abort(404, message=msg)
            game['_id'] = game_id
            return jsonify(game)

    @jwt_required
    def post(self):
        """REST endpoint that creates a new game."""
        if request.get_json() is None:
            return abort(400, 'Must conatin body with username in post request.')

        num_players = request.get_json().get('num_players')
        if num_players is None:
            msg = 'Missing required arg num_players'
            return abort(400, message=msg)

        game_name = request.get_json().get('game_name', False)
        if game_name is None:
            msg = 'Missing required arg game_name'
            return abort(400, message=msg)

        with_rainbow = request.get_json().get('with_rainbow', False)

        game = Game(int(num_players), with_rainbow, name=game_name)
        game.start_game()
        games = rest.database.db.games
        _id = games.insert_one(game.dict).inserted_id
        rest.database.db.users.update({'_id': ObjectId(get_jwt_identity())}, {
            '$addToSet': {
                'owns': {'game': ObjectId(_id), 'player_id': 0}
            }
        }, upsert=False)
        rest.database.db.metagames.insert_one({
            'game_id': ObjectId(_id),
            'turn': game.turn,
            'game_name': game.name,
            'num_hints': game.num_hints,
            'num_errors': game.num_errors,
            'owner': ObjectId(get_jwt_identity()),
            'num_players': int(num_players),
            'players': [ObjectId(get_jwt_identity())]
        })
        socket.emit_to_client('game_created', {'name': game.name, 'id': str(_id)})
        return jsonify(str(_id))

    def delete(self, game_id=None):
        """REST endpoint that removes all or one game."""
        if game_id is not None:
            rest.database.db.metagames.remove({'game_id': ObjectId(game_id)})
            rest.database.db.games.remove({'_id': ObjectId(game_id)})
            users = []
            for user in rest.database.db.users.find({'owns.game': ObjectId(game_id)}):
                users.append(remove_object_ids_from_dict(user))
            for user in users:
                for i, game in enumerate(user['owns']):
                    if game['game'] == game_id:
                        del user['owns'][i]
                user_without_id = {k: v for k, v in user.items() if k != '_id'}
                rest.database.db.users.update({'_id': ObjectId(user['_id'])}, user_without_id)

            socket.emit_to_client('game_deleted', game_id)
        else:
            rest.database.db.metagames.remove()
            rest.database.db.games.remove()
        return Response('', status=204, mimetype='application/json')


class MetaGames(flask.views.MethodView):
    """Class containing REST methods for the ``/meta/game`` endpoint."""

    @jwt_required
    def get(self, meta_game_id=None):
        """REST endpoint that gets the current state of a game with a provided id."""
        LOGGER.info("Hitting REST endpoint: '/meta/game'")

        if meta_game_id is None:
            games = []
            for game in rest.database.db.metagames.aggregate([
                {
                    '$lookup': {
                    'from': 'users',
                    'localField': 'owner',
                    'foreignField': '_id',
                    'as': 'owner'
                    }
                },
                {
                    '$lookup': {
                    'from': 'users',
                    'localField': 'players',
                    'foreignField': '_id',
                    'as': 'players'
                    }
                }
            ]):
                game = remove_object_ids_from_dict(game)
                games.append(game)
            return jsonify(games)
        else:
            game = rest.database.db.metagames.find_one({'_id': ObjectId(meta_game_id)})
            if game is None:
                msg = 'Game cannot be found.'
                return abort(make_response(jsonify(message=msg), 400))
            game['_id'] = meta_game_id
            return jsonify(game)
