"""Defines logic used for the endpoints found at ``/authenticate``."""
import logging

import flask
import flask.views
from flask import request
from flask_restplus import abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from api import rest
from api.config.config import Config

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
        return flask.jsonify({'msg': ('Congratulations on having a valid JWT, {}.'
                                      .format(get_jwt_identity()))})

    def post(self):
        """REST endpoint that authenticates a username."""
        if request.get_json() is None:
            return abort(400, 'Must conatin body with username in post request.')

        username = request.get_json().get('username')

        if username is None:
            return abort(400, 'Username must be present in body.')

        users = []
        for user in rest.database.db.users.find({'name': username}):
            users.append(user)
        if len(users) == 0:
            # create a user
            user = {'games': [], 'owns': [], 'name': username}
            rest.database.db.users.insert_one(user)
        else:
            LOGGER.info(f"User {username} alrady exists in the database.")

        LOGGER.info(f"Hitting REST endpoint: '/authenticate' with user: {username}")
        token = create_access_token(identity=username)
        LOGGER.debug('Generated access token for {}: {}'.format(username,
                                                                token))
        return flask.jsonify({'token': token})
