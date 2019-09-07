"""Defines logic used for the endpoints found at ``/haiku``."""
import logging
import flask
import flask.views
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, Response
from flask_restplus import abort
from bson.objectid import ObjectId

from hanabi.game import Game
from hanabiapi.utils import socket
from hanabiapi.api import rest
from hanabiapi import decorators
from hanabiapi.utils.database import remove_object_ids_from_dict
from hanabiapi.utils.rest import get_body
import hanabiapi.exceptions as exceptions

from hanabiapi.datastores.mongo.factory import DAOFactory

LOGGER = logging.getLogger(__name__)


class Games(flask.views.MethodView):
    """Class containing REST methods for the ``/game`` endpoint."""

    def __init__(self):
        """Init attributes for a ``Games`` object."""
        self.dao = DAOFactory().create_game_dao()

    @jwt_required
    @decorators.check_keys(required_keys=[], optional_keys=[])
    def get(self, game_id=None):
        """
        REST endpoint that gets the current state of a game with a provided id.

        This is a ``@jwt_required`` protected endpoint.

        :param game_id: Id of the game to get.

        :returns: A ``flask.Response`` object that contains one of the following:

            - If successfully retrieved and game_id is not specified:

                ``200`` status code and a body containing a list of games with the following form:

                .. code-block:: json

                [
                    {
                        "name": "-- game name--",
                        "id": "--valid game id--"
                    }
                ]

            - If successfully retrieved and game_id is specified:

                ``200`` status code and a body containin a single game of this form:

                .. code-block:: json

                    {
                        "_id": "-- some valid game id--",
                        "available_pieces": [
                            "-- a list of ``Piece`` objects as json --"
                        ],
                        "binned_pieces": [
                            "-- a list of ``Piece`` objects as json --"
                        ],
                        "name": "-- the name of the game --",
                        "num_errors": "-- the number of errors as an integer--",
                        "num_hints": "-- the number of hints as an integer--",
                        "played_pieces": [
                            "-- a list of ``Piece`` objects as json --"
                        ],
                        "players": [
                            "-- a list of ``Player`` objects as json --"
                        ]
                    }

            - If ``game_id`` cannot be found:

                ``404`` status code.

            - If unauthorized (invalid JWT):

                ``401`` status code and a body containing a message stating the user is not
                authorized.
        """
        LOGGER.info("Hitting REST endpoint: '/game'")

        if game_id is None:
            LOGGER.debug("Getting list of games.")
            games = self.dao.read()
            return jsonify(games)
        else:
            LOGGER.debug("Getting a single game.")

            try:
                game = self.dao.read(_id=game_id)
            except exceptions.GameNotFound as gnf:
                LOGGER.debug(gnf.message)
                return abort(404, message=gnf.message)

            game['_id'] = game_id
            return jsonify(game)

    @jwt_required
    @decorators.check_keys(
        required_keys=[
            {
                'key': 'game_name',
                'type': "<class 'str'>"
            },
            {
                'key': 'num_players',
                'type': "<class 'int'>"
            }
        ], optional_keys=[
            {
                'key': 'with_rainbow',
                'type': "<class 'bool'>"
            }
        ], check_request_body=True)
    def post(self):
        """
        REST endpoint that creates a new game.

        This is a ``@jwt_required`` protected endpoint.

        The current ``flask.request`` object should contain the following:

            **Required**:

                - ``request.data['game_name']`` The name of the game.

                - ``request.data['num_players']`` The number of players in the game.

            **Optional**:

                - ``request.data['with_rainbow']`` Whether or not the game should be played with
                    rainbow tiles.

        :returns: A ``flask.Response`` object that contains one of the following:

            - If game successfully created:

                ``201`` status code and a body containing the id of the game:

            - If ``num_players`` not provided in request.data:

                ``400`` status code.

            - If ``game_name`` not provided in request.data:

                ``400`` status code.

            - If unauthorized (invalid JWT):

                ``401`` status code and a body containing a message stating the user is not
                authorized.
        """
        body = get_body(is_required=True)

        game_name = body.get('game_name')
        num_players = body.get('num_players')
        with_rainbow = body.get('with_rainbow', False)

        LOGGER.debug("Creating instance of game.")
        game = Game(int(num_players), with_rainbow, name=game_name)
        game.start_game()

        LOGGER.debug("Inserting game into database.")
        _id = self.dao.create(get_jwt_identity(), game.dict)

        socket.emit_to_client('game_created', {'name': game.name, 'id': str(_id)})
        return jsonify(_id)

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
                return abort(400, msg)
            game['_id'] = meta_game_id
            return jsonify(game)
