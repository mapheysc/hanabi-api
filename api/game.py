"""Defines logic used for the endpoints found at ``/haiku``."""
import logging
import uuid
import flask
import json
import flask.views
from flask import abort, make_response, jsonify, request, Response
from flask_restplus import abort
import pymongo
from bson.objectid import ObjectId

from hanabi.game import Game
from utils import socket
from api import rest
LOGGER = logging.getLogger(__name__)


class Games(flask.views.MethodView):
    """Class containing REST methods for the ``/game`` endpoint."""

    def get(self, game_id=None):
        """
        REST endpoint that gets the current state of a game with a provided id.
        """
        LOGGER.info("Hitting REST endpoint: '/game'")

        if game_id is None:
            return jsonify([{'name': game['name'], 'id': str(game['_id'])} for game in rest.database.db.games.find()])
        else:
            game = rest.database.db.games.find_one({'_id': ObjectId(game_id)})
            if game is None:
                msg = 'Game cannot be found.'
                return abort(404, message=msg)
            game['_id'] = game_id
            return jsonify(game)

    def post(self):
        num_players = request.args.get('num_players')
        if num_players is None:
            msg = 'Missing required arg num_players'
            return abort(400, message=msg)
        user_id = request.args.get('user_id')
        if user_id is None:
            msg = 'Missing required arg user_id'
            return abort(400, message=msg)
        with_rainbow = request.args.get('with_rainbows', '')
        game_name = request.args.get('game_name')
        if with_rainbow.lower() == 'true':
            with_rainbow = True

        game = Game(int(num_players), with_rainbow, name=game_name)
        game.start_game()
        games = rest.database.db.games
        _id = games.insert_one(game.dict).inserted_id
        rest.database.db.users.update({'_id': ObjectId(user_id)}, {
            '$addToSet': {
                'own': str(_id)
            }
        }, upsert=False)
        rest.database.db.metagames.insert_one({
            'game_id': str(_id),
            'owner': user_id,
            'num_players': num_players,
            'players': [user_id]
        })
        socket.emit_to_client('game_created', {'name': game.name, 'id': str(_id)})
        return jsonify(str(_id))

    def delete(self, game_id=None):
        rest.database.db.games.remove({'_id': ObjectId(game_id)})
        return Response('', status=204, mimetype='application/json')


class MetaGames(flask.views.MethodView):
    """Class containing REST methods for the ``/meta/game`` endpoint."""

    def get(self, meta_game_id=None):
        """
        REST endpoint that gets the current state of a game with a provided id.
        """
        LOGGER.info("Hitting REST endpoint: '/meta/game'")

        if meta_game_id is None:
            games = []
            for game in rest.database.db.metagames.find():
                game.update(_id=str(game['_id']))
                games.append(game)
            return jsonify(games)
        else:
            game = rest.database.db.metagames.find_one({'_id': ObjectId(meta_game_id)})
            if game is None:
                msg = 'Game cannot be found.'
                return abort(make_response(jsonify(message=msg), 400))
            game['_id'] = meta_game_id
            return jsonify(game)
