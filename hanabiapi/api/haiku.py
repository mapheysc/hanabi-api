"""Defines logic used for the endpoints found at ``/haiku``."""
import logging

import flask
import flask.views


import hanabiapi.utils.haiku as haikus

LOGGER = logging.getLogger(__name__)


class Haiku(flask.views.MethodView):
    """Class containing REST methods for the ``/haiku`` endpoint."""

    def get(self):
        """
        REST endpoint that generates a random haiku.

        :returns: A ``flask.Response`` object that contains the following:

            - ``200`` status code and a body containing a haiku. For example:

              .. code-block:: json

                {
                    "author": "Kobayashi Issa",
                    "haiku": "Hi! My little hut"
                             "is newly-thatched I see..."
                             "Blue morning-glories"
                }
        """
        LOGGER.info("Hitting REST endpoint: '/haiku'")
        try:
            return flask.jsonify(haikus.generate_haiku())
        except FileNotFoundError:
            return flask.jsonify('Unable to generate a haiku.')
