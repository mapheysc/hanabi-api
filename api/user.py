"""Defines logic used for the endpoints found at ``/haiku``."""
import logging
import uuid
import flask
import json
import flask.views
from flask import make_response, jsonify, request, Response
from flask_restplus import abort
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
        player_name = request.args.get('player_name', 'Anonymous')
        if user_id is None:
            if game_id is None:
                if player_name == 'Anonymous':
                    users = []
                    for user in rest.database.db.users.find():
                        user.update(_id=str(user['_id']))
                        users.append(user)
                    return jsonify(users)
                if player_name != 'Anonymous':
                    users = []
                    for user in rest.database.db.users.find({'name': player_name}):
                        user.update(_id=str(user['_id']))
                        users.append(user)
                    if len(users) == 1:
                        return jsonify(users[0])
                    elif len(users) == 0:
                        return abort(404, message='User with that name does not exist.')
                    else:
                        return abort(400, message='A user with this name already exists.')
            else:
                return jsonify([user for user in rest.database.db.users.find({'game_ids': game_id})])
        else:
            user = rest.database.db.users.find_one({'_id': ObjectId(user_id)})
            if user is None:
                msg = 'User cannot be found.'
                return abort(404, message=msg)
            user['_id'] = user_id
            return jsonify(user)

    def post(self):
        player_name = request.args.get('player_name', 'Anonymous')
        if player_name != 'Anonymous':
            users = []
            for user in rest.database.db.users.find({'name': player_name}):
                users.append(user)
            if len(users) > 0:
                return abort(400, 'User with that name already exists.')
        user = {'game_ids': [], 'owns': [], 'name': player_name}
        _id = rest.database.db.users.insert_one(user).inserted_id
        return jsonify(str(_id))

    def put(self, user_id=None):
        user = rest.database.db.users.find_one({'_id': ObjectId(user_id)})
        game_id = request.args.get('game_id')
        own = request.args.get('own')
        player_id = request.args.get('player_id')
        if rest.database.db.games.find_one({'_id': ObjectId(own)}) is not None:
            user['owns'].append({'game': own, 'player_id': player_id})
            rest.database.db.users.update({'_id': ObjectId(user_id)}, user)
            return Response('', status=204, mimetype='application/json')
        elif rest.database.db.games.find_one({'_id': ObjectId(game_id)}) is not None:
            user['game_ids'].append({'game': game_id, 'player_id': player_id})
            rest.database.db.users.update({'_id': ObjectId(user_id)}, user)
            return Response('', status=204, mimetype='application/json')
        else:
            msg = 'Game cannot be found.'
            return abort(404, message=msg)

    def delete(self, user_id=None):
        if user_id is not None:
            rest.database.db.users.remove({'_id': ObjectId(user_id)})
        else:
            rest.database.db.users.remove()
        return Response('', status=204, mimetype='application/json')
