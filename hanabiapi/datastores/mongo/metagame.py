"""Defines objects to be used for interacting with metagames from a Mongo database."""
import logging
from bson.objectid import ObjectId

from hanabiapi.api import rest
from hanabiapi.datastores.dao import MetaGameDAO

LOGGER = logging.getLogger(__name__)


class MongoMetaGameDAO(MetaGameDAO):
    """DAO responsible for interacting with metagames in Mongo."""

    def __init__(self):
        """Initialize the ``MetaGameDAO`` object."""

    def search(self, **kwargs):
        """
        Search for meta games.

        :param kwargs: Keyword arguments to specify how to search.
        :returns: A list of meta games that match to search criteria.
        """
        raise NotImplementedError

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

    def create(self, meta_game):
        """
        Create a new meta game.

        :param meta_game: A dictionary representation of a meta game.
        :returns: The id of the newly created meta game.
        """
        # Convert the ids to mongo accepted ids
        meta_game['game_id'] = ObjectId(meta_game['game_id'])
        meta_game['owner'] = ObjectId(meta_game['owner'])
        meta_game['num_players'] = int(meta_game['num_players'])
        meta_game['players'][0] = ObjectId(meta_game['players'][0])

        return rest.database.db.metagames.insert_one(meta_game).inserted_id

    def update(self, id, meta_game):
        """
        Update a meta game.

        :param id: The id of the meta game to update.
        :param game: A dictionary representation of a meta game.
        :returns: None.
        """
        raise NotImplementedError

    def delete(self, id=None):
        """
        Delete a meta game.

        If id is None delete all meta games.

        :param id: The id of the meta game to delete.
        :returns: None.
        """
        raise NotImplementedError
