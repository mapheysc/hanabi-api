"""Defines logic used for the endpoints found at ``/haiku``."""
import logging
import uuid
import flask
import json
import flask.views
from flask import abort, make_response, jsonify, request, Response
import pymongo
from bson.objectid import ObjectId

from hanabi.game import Game
from utils import socket
from api import rest
LOGGER = logging.getLogger(__name__)


class Users(flask.views.MethodView):
    """Class containing REST methods for the ``/user`` endpoint."""

    def get(self, user_id=None):
        """
        REST endpoint that gets the current state of a user with a provided id.
        """
        LOGGER.info("Hitting REST endpoint: '/user'")

        game_id = request.args.get('game_id')
        if user_id is None:
            if game_id is None:
                return jsonify(rest.database.db.users.find())
            else:
                return jsonify(rest.database.db.users.find({'game_ids': game_id}))
        else:
            user = rest.database.db.users.find_one({'_id': ObjectId(user_id)})
            if user is None:
                msg = 'User cannot be found.'
                return abort(make_response(jsonify(message=msg), 400))
            user['_id'] = user_id
            return jsonify(user)

    def post(self, player_name='Anonymous', user_id=None):
        if user_id is None:
            user = {'game_ids': [], 'owns': [], 'name': player_name}
            _id = rest.database.db.users.insert_one(user).inserted_id
            return jsonify(str(_id))
        else:
            user = rest.database.db.users.find_one({'_id': ObjectId(user_id)})
            game_id = request.args.get('game_id')
            own = request.args.get('own')
            if rest.database.db.games.find_one({'_id': ObjectId(own)}) is not None:
                user['owns'].append(own)
                rest.database.db.users.update({'_id': ObjectId(user_id)}, user)
                return Response('', status=204, mimetype='application/json')
            elif rest.database.db.games.find_one({'_id': ObjectId(game_id)}) is not None:
                user['game_ids'].append(game_id)
                rest.database.db.users.update({'_id': ObjectId(user_id)}, user)
                return Response('', status=204, mimetype='application/json')
            else:
                msg = 'Game cannot be found.'
                return abort(make_response(jsonify(message=msg), 400))

    def delete(self, user_id):
        rest.database.db.users.remove({'_id': ObjectId(user_id)})
        return Response('', status=204, mimetype='application/json')
