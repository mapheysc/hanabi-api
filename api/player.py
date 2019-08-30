import logging
import uuid
import flask
import json
import flask.views
from flask import abort, make_response, jsonify, request, Response
from addict import Dict
from bson.objectid import ObjectId
from flask_restplus import abort


from hanabi.game import Game
from hanabi.piece import Color
from utils import socket
from api import rest

import hanabi.exceptions as exc

LOGGER = logging.getLogger(__name__)

class Players(flask.views.MethodView):
    """Class containing REST methods for the ``/player`` endpoint."""

    def __init__(self):
        """Init attributes for a Haiku object."""

    def get(self, player_id):
        """
        REST endpoint that gets the current state of a game with a provided id.
        """
        LOGGER.info("Hitting REST endpoint: '/player'")
        game_id = request.args.get('game_id')

        if game_id is None:
            msg = 'Missing required arg game_id'
            return flask.abort(make_response(jsonify(message=msg), 400))

        if player_id is None:
            msg = 'Missing required arg player_id'
            return flask.abort(make_response(jsonify(message=msg), 400))
        try:
            game = rest.database.db.games.find_one({"_id": ObjectId(game_id)})
        except KeyError as ke:
            msg = 'Game could not be found.'
            return flask.abort(make_response(jsonify(message=msg), 400))
        if game is not None:
            players = game.get('players')
        else:
            msg = 'Game could not be found.'
            return flask.abort(make_response(jsonify(message=msg), 400))
        if player_id.isdigit():
            player = next((p for p in players if p['id'] == int(player_id)), None)
            if player is None:
                msg = 'Player was not found'
                return flask.abort(make_response(jsonify(message=msg), 400))
        else:
            return abort(400, 'Player is not an integer')

        return jsonify(player)

    def post(self, player_id):
        game_id = request.args.get('game_id')
        hint = request.args.get('hint')
        affected_player = request.args.get('affected_player')
        game = Game.from_json(Dict(rest.database.db.games.find_one({'_id': ObjectId(game_id)})))

        if game_id is None:
            msg = 'Missing required arg game_id'
            return flask.abort(make_response(jsonify(message=msg), 400))

        if player_id is None:
            msg = 'Missing required arg player_id'
            return flask.abort(make_response(jsonify(message=msg), 400))
        player = next((p for p in game.players if p.id == int(player_id)), None)
        if player is None:
            msg = 'Player was not found'
            return flask.abort(make_response(jsonify(message=msg), 400))
        if hint is not None:
            affected_player = game.players[int(affected_player)]
            try:
                if hint in Color.COLORS:
                    game.players[int(player_id)].hint_action_give_color(color=hint, affected_player=affected_player)
                else:
                    game.players[int(player_id)].hint_action_give_number(number=int(hint), affected_player=affected_player)
            except exc.HintException as he:
                msg = 'Not enough hints to give.'
                return flask.abort(make_response(jsonify(message=msg), 400))
            except exc.NotPlayersTurn as he:
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


