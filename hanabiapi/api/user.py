"""Defines logic used for the endpoints found at ``/user``."""
import logging
import flask
import flask.views
from flask import jsonify, request, Response
from flask_restplus import abort
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required

from hanabiapi.utils.database import remove_object_ids_from_dict
from hanabiapi.api import rest

from hanabiapi.datastores.mongo.factory import DAOFactory

LOGGER = logging.getLogger(__name__)


class Users(flask.views.MethodView):
    """Class containing REST methods for the ``/user`` endpoint."""

    def __init__(self):
        """Init attributes for a ``Users`` object."""
        self.dao = DAOFactory().create_user_dao()

    @jwt_required
    def get(self, user_id=None):
        """REST endpoint that gets the current state of a user with a provided id."""
        LOGGER.info("Hitting REST endpoint: '/user'")

        game_id = request.args.get('game_id')
        player_name = request.args.get('player_name', 'Anonymous')
        aggregator = []
        if user_id is None:
            if game_id is None:
                if player_name == 'Anonymous':
                    users = []
                    for user in rest.database.db.users.find():
                        users.append(remove_object_ids_from_dict(user))
                    return jsonify(users)
                if player_name != 'Anonymous':
                    users = []
                    for user in rest.database.db.users.find({'name': player_name}):
                        users.append(remove_object_ids_from_dict(user))
                    if len(users) == 1:
                        user = remove_object_ids_from_dict(users[0])
                        return jsonify(user)
                    elif len(users) == 0:
                        return abort(404, message='User with that name does not exist.')
                    else:
                        return abort(400, message='A user with this name already exists.')
            else:
                return jsonify([user for user in rest.database.db.users.find({'games': game_id})])
        else:
            users = []
            aggregator.append({
                '$match': {
                    '_id': ObjectId(user_id)
                }
            })
            for user in rest.database.db.users.aggregate(aggregator):
                user = remove_object_ids_from_dict(user)
                users.append(user)

            if len(users) == 0:
                msg = 'User cannot be found.'
                return abort(404, message=msg)
            return jsonify(users[0])

    @jwt_required
    def put(self, user_id=None):
        """REST endpoint that updates a user."""
        user = rest.database.db.users.find_one({'_id': ObjectId(user_id)})
        meta_game_id = request.args.get('meta_game_id')
        meta_game = rest.database.db.metagames.find_one({'_id': ObjectId(meta_game_id)})
        if meta_game is not None:
            if len(meta_game['players']) == meta_game['num_players']:
                return abort(400, 'Game already has max amount of players')
            if ObjectId(user_id) in meta_game['players']:
                return abort(400, 'You are already in the game.')
            user['games'].append(
                {'game': ObjectId(meta_game['game_id']), 'player_id': len(meta_game['players'])})
            rest.database.db.users.update({'_id': ObjectId(user_id)}, user)
            meta_game = rest.database.db.metagames.update({'_id': ObjectId(meta_game_id)}, {
                '$addToSet': {
                    'players': ObjectId(user_id)
                }
            })
            return Response('', status=204, mimetype='application/json')
        else:
            msg = 'Game cannot be found.'
            return abort(404, message=msg)

    @jwt_required
    def delete(self, user_id=None):
        """REST endpoint that deletes a user or list of users."""
        if user_id is not None:
            rest.database.db.users.remove({'_id': ObjectId(user_id)})
        else:
            rest.database.db.users.remove()
        return Response('', status=204, mimetype='application/json')
