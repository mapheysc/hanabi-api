"""Defines logic used for the endpoints found at ``/player``."""

import logging
import flask
import flask.views
from flask import make_response, jsonify, request
from addict import Dict
from bson.objectid import ObjectId
from flask_restplus import abort
from flask_jwt_extended import jwt_required
import hanabi.exceptions as exc
from hanabi.game import Game
from hanabi.piece import Color

from hanabiapi.utils import socket
from hanabiapi.api import rest

LOGGER = logging.getLogger(__name__)


class Players(flask.views.MethodView):
    """Class containing REST methods for the ``/player`` endpoint."""

    @jwt_required
    def get(self, player_id):
        """REST endpoint that gets the current state of a game with a provided id."""
        LOGGER.info("Hitting REST endpoint: '/player'")
        game_id = request.args.get('game_id')

        if game_id is None:
            msg = 'Missing required arg game_id'
            return abort(400, msg)

        if player_id is None:
            msg = 'Missing required arg player_id'
            return abort(400, msg)
        try:
            game = rest.database.db.games.find_one({"_id": ObjectId(game_id)})
        except KeyError:
            msg = 'Game could not be found.'
            return abort(400, msg)
        if game is not None:
            players = game.get('players')
        else:
            msg = 'Game could not be found.'
            return abort(400, msg)
        if player_id.isdigit():
            player = next((p for p in players if p['id'] == int(player_id)), None)
            if player is None:
                msg = 'Player was not found'
                return abort(400, msg)
        else:
            return abort(400, 'Player is not an integer')

        return jsonify(player)

    @jwt_required
    def post(self, player_id):
        """REST endpoint that creates a hint for a player."""
        game_id = request.args.get('game_id')
        hint = request.args.get('hint')
        affected_player = request.args.get('affected_player')
        game = Game.from_json(Dict(rest.database.db.games.find_one({'_id': ObjectId(game_id)})))

        if game_id is None:
            msg = 'Missing required arg game_id'
            return abort(400, msg)

        if player_id is None:
            msg = 'Missing required arg player_id'
            return abort(400, msg)
        player = next((p for p in game.players if p.id == int(player_id)), None)
        if player is None:
            msg = 'Player was not found'
            return abort(400, msg)
        if hint is not None:
            affected_player = game.players[int(affected_player)]
            try:
                if hint in Color.COLORS:
                    game.players[
                        int(player_id)
                    ].hint_action_give_color(color=hint, affected_player=affected_player)
                else:
                    game.players[
                        int(player_id)
                    ].hint_action_give_number(number=int(hint), affected_player=affected_player)
            except exc.HintException:
                msg = 'Not enough hints to give.'
                return flask.abort(make_response(jsonify(message=msg), 400))
            except exc.NotPlayersTurn:
                return abort(400, 'Not your turn.')
            socket.emit_to_client(
                'player_updated',
                {
                    'player': game.players[affected_player.id].dict,
                    'acting_player': player.name
                }
            )
        rest.database.db.games.update({'_id': ObjectId(game_id)}, game.dict)
        socket.emit_to_client(
            'game_updated',
            {
                'id': game_id,
                'game': game.dict
            }
        )
        return jsonify(game.dict)
