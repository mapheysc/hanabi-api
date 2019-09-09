"""
Contains top-level abstract DAOs for accessing data for Hanabi.

DAOs contained herein may differ from available functionality, but they will not differ between
backends.
"""
from abc import ABCMeta, abstractmethod
import logging

LOGGER = logging.getLogger(__name__)


class UtilsDAO(object):
    """The DAO responseible for handling necessary utility functions."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def populate(obj):
        """Replace any reference field with a json representation."""
        raise NotImplementedError


class GameDAO(object):
    """The DAO responseible for handling ``Game`` objects."""

    __metaclass__ = ABCMeta

    def __init__(self):
        """Initialize the ``MetaGameDAO`` object."""
        raise NotImplementedError

    @abstractmethod
    def search(self, **kwargs):
        """
        Search for games.

        :param kwargs: Keyword arguments to specify how to search.
        :returns: A list of games that match to search criteria.
        """
        raise NotImplementedError

    @abstractmethod
    def read(self, id=None):
        """
        Read a game.

        If id is None read all games.

        :param id: The id of the game to read.
        :returns:

            - If id is not None:

                A dictionary representation of a game
                built from the hanabi game engine.

            - If id is None:

                A list of games.
        """
        raise NotImplementedError

    @abstractmethod
    def create(self, user, game):
        """
        Create a new game.

        :param user: The user who created the game.
        :param game: A dictionary representation of a game
            built from the hanabi game engine.
        :returns: The id of the newly created game.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, id, game):
        """
        Update a game.

        :param id: The id of the game to update.
        :param game: A dictionary representation of a game
            built from the hanabi game engine.
        :returns: None.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, user, id=None):
        """
        Delete a game.

        If id is None delete all games.

        :param user: The user who deleted the game.
        :param id: The id of the game to delete.
        :returns: None.
        """
        raise NotImplementedError


class MetaGameDAO(object):
    """The DAO responseible for handling ``MetaGame`` objects."""

    __metaclass__ = ABCMeta

    def __init__(self):
        """Initialize the ``MetaGameDAO`` object."""
        raise NotImplementedError

    @abstractmethod
    def search(self, **kwargs):
        """
        Search for meta games.

        :param kwargs: Keyword arguments to specify how to search.
        :returns: A list of meta games that match to search criteria.
        """
        raise NotImplementedError

    @abstractmethod
    def read(self, id=None):
        """
        Read a meta game.

        If id is None get all games.

        :param id: The id of the meta game to read.
        :returns:

            - If id is not None:

                A dictionary representation of a meta game.

            - If id is None:

                A list of meta games.
        """
        raise NotImplementedError

    @abstractmethod
    def create(self, meta_game):
        """
        Create a new meta game.

        :param meta_game: A dictionary representation of a meta game.
        :returns: The id of the newly created meta game.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, id, meta_game):
        """
        Update a meta game.

        :param id: The id of the meta game to update.
        :param game: A dictionary representation of a meta game.
        :returns: None.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, id=None):
        """
        Delete a meta game.

        If id is None delete all meta games.

        :param id: The id of the meta game to delete.
        :returns: None.
        """
        raise NotImplementedError


class UserDAO(object):
    """The DAO responseible for handling ``User`` objects."""

    __metaclass__ = ABCMeta

    def __init__(self):
        """Initialize the ``UserDAO`` object."""
        raise NotImplementedError

    @abstractmethod
    def search(self, **kwargs):
        """
        Search for users.

        :param kwargs: Keyword arguments to specify how to search.
        :returns: A list of users that match to search criteria.
        """
        raise NotImplementedError

    @abstractmethod
    def read(self, id=None):
        """
        Read a user.

        If id is not specified return a list of all users.

        :param id: The id of the user to read.
        :returns:

            - If id is not None:

                A dictionary representation of a user.

            - If id is None:

                A list of users.
        """
        raise NotImplementedError

    @abstractmethod
    def create(self, game):
        """
        Create a new user.

        :param user: A dictionary representation of a user.
        :returns: The id of the newly created user.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, id, user):
        """
        Update a user.

        :param id: The id of the user to update.
        :param game: A dictionary representation of a user.
        :returns: None.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, id=None):
        """
        Delete a user.

        If id is None delete all users.

        :param id: The id of the user to delete.
        :returns: None.
        """
        raise NotImplementedError


class DAOFactory(object):
    """Builds ``DAO`` objects used for interacting with backends."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def create_game_dao():
        """
        Create a ``DAO`` for interacting with ``Game`` objects.

        :returns: A ``GameDAO`` for the ``DAOFactory``'s backend.
        """
        raise NotImplementedError

    @abstractmethod
    def create_user_dao():
        """
        Create a ``DAO`` for interacting with ``User`` objects.

        :returns: A ``UserDAO`` for the ``DAOFactory``'s backend.
        """
        raise NotImplementedError

    @abstractmethod
    def create_metagame_dao():
        """
        Create a ``DAO`` for interacting with ``MetaGame`` objects.

        :returns: A ``MetaGame`` for the ``DAOFactory``'s backend.
        """
        raise NotImplementedError
