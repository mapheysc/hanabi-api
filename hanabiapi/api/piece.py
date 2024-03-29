"""Module for managing pieces."""
import logging
import flask
import flask.views
from flask import jsonify, request
from addict import Dict
from bson.objectid import ObjectId
from flask_restplus import abort

import hanabi.exceptions as exc
from hanabi.game import Game
from hanabiapi.utils import socket
from hanabiapi.api import rest

LOGGER = logging.getLogger(__name__)


class Pieces(flask.views.MethodView):
    """Class containing REST methods for the ``/piece`` endpoint."""

    def __init__(self):
        """Init attributes for a Haiku object."""

    def get(self, piece_id):
        """REST endpoint that gets the current state of a game with a provided id."""
        LOGGER.info("Hitting REST endpoint: '/piece'")
        game_id = request.args.get('game_id')

        if game_id is None:
            msg = 'Missing required arg game_id'
            return abort(400, msg)

        game = Game.from_json(Dict(rest.database.db.games.find_one({'_id': ObjectId(game_id)})))

        return jsonify(game.get_piece(piece_id).dict)

    def post(self, piece_id):
        """REST endpoint that creates an action on a new piece."""
        game_id = request.args.get('game_id')
        player_id = request.args.get('player_id')
        action = request.args.get('action')

        if game_id is None:
            msg = 'Missing required arg game_id'
            return abort(400, msg)

        if player_id is None:
            msg = 'Missing required arg player_id'
            return abort(400, msg)

        if action != 'play' and action != 'discard':
            msg = 'Action not recognized. Must be either play or discard.'
            return abort(400, msg)

        game = Game.from_json(Dict(rest.database.db.games.find_one({'_id': ObjectId(game_id)})))
        player = game.players[int(player_id)]
        piece = game.get_piece(piece_id)

        try:
            if action == 'play':
                try:
                    player.play_piece(piece)
                except exc.YouLoseGoodDaySir:
                    msg = 'You have lost the game.'
                    game.has_finished = True
                    rest.database.db.games.update({'_id': ObjectId(game_id)}, game.dict)
                    socket.emit_to_client('game_updated', {'id': game_id, 'game': game.dict})
                    return abort(400, msg)
                except exc.NotPlayersTurn:
                    msg = 'It is not your turn'
                    return abort(400, msg)

                msg = 'Successfully played piece.'
                if piece in game.binned_pieces:
                    msg = 'Failed to play piece. It is now discarded.'
            else:
                player.remove_piece(piece)
                msg = 'Successfully removed piece.'
        except ValueError:
            msg = 'Player no longer has piece.'
            return abort(400, msg)

        rest.database.db.games.update({'_id': ObjectId(game_id)}, game.dict)
        socket.emit_to_client('game_updated', {'id': game_id, 'game': game.dict})

        return jsonify(msg)
