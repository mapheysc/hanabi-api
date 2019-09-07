"""Utility functions for sockets."""
import logging

from hanabiapi.api import rest

LOGGER = logging.getLogger(__name__)


def emit_to_client(message, data=None, room=None):
    """
    Util function for emitting a message and data to the client.

    :param message: The message being emitted to client.
    :param data: The data being emitted in the form of a dict.
    :param room: The room to emit to.
    """
    rest.socketio.emit(message, data, room=room)
