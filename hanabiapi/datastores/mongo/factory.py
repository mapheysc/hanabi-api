"""Defines objects and functions to be used for creating MarkLogic DAOs."""
import logging
import hanabiapi.datastores.dao as dao
from hanabiapi.datastores.mongo.game import MongoGameDAO
from hanabiapi.datastores.mongo.user import MongoUserDAO
from hanabiapi.datastores.mongo.metagame import MongoMetaGameDAO

LOGGER = logging.getLogger(__name__)


class DAOFactory(dao.DAOFactory):
    """
    Build Mongo-backed DAOs.

    Includes ``User``, ``Game``, and ``MetaGame`` DAO objects.
    """

    def create_game_dao(self):
        """
        Create a DAO for interacting with ``Game`` objects.

        :returns: A ``GameDAO`` for a Mongo backend.
        """
        return MongoGameDAO()

    def create_user_dao(self):
        """
        Create a DAO for interacting with ``User`` objects.

        :returns: A ``UserDAO`` for a Mongo backend.
        """
        return MongoUserDAO()

    def create_meta_game_dao(self):
        """
        Create a DAO for interacting with ``MetaGame`` objects.

        :returns: A ``MetaGameDAO`` for a Mongo backend.
        """
        return MongoMetaGameDAO()

    def __repr__(self):
        """
        Return a string representation of a Mongo DAOFactory.

        :returns: The string representation of a Mongo ``DAOFactory`` object.
        """
        return 'Mongo DAOFactory <ip={}>'.format(self.ip)
