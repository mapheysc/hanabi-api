"""Defines logic used for the endpoints found at ``/authenticate``."""
import logging

import flask
import flask.views
from flask import request
from flask_restplus import abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from hanabiapi.api import rest
from hanabiapi.api.config.config import Config

LOGGER = logging.getLogger(__name__)


class Authenticate(flask.views.MethodView):
    """Class containing REST methods for the ``/authenticate`` endpoint."""

    def __init__(self):
        """Init attributes for an Authenticate object."""
        self.CONFIG = Config()

    @jwt_required
    def get(self):
        """REST endpoint that checks if the given JWT is valid."""
        LOGGER.info("GET for endpoint: '/authenticate'")
        return flask.jsonify({'id': get_jwt_identity()})

    def post(self):
        """REST endpoint that authenticates a username."""
        if request.get_json() is None:
            return abort(400, 'Must conatin body with username in post request.')

        username = request.get_json().get('username')
        LOGGER.debug(f'Creating auth token for {username}')

        if username is None:
            return abort(400, 'Username must be present in body.')

        users = []
        existed = True
        for user in rest.database.db.users.find({'name': username}):
            users.append(user)
        if len(users) == 0:
            existed = False
            # create a user
            user = {'games': [], 'owns': [], 'name': username}
            _id = rest.database.db.users.insert_one(user).inserted_id
        else:
            LOGGER.info(f"User {username} already exists in the database.")
            if len(users) > 1:
                return abort(500, 'There are too many users with the same username.')
            else:
                _id = users[0]['_id']

        LOGGER.info(f"Hitting REST endpoint: '/authenticate' with user: {username}")
        token = create_access_token(identity=str(_id))
        LOGGER.debug('Generated access token for {}: {}'.format(username,
                                                                token))
        return flask.jsonify({'token': token, 'existed': existed})
