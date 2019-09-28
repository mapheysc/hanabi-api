"""Defines objects to be used for interacting with metagames from a Mongo database."""
import logging
from bson.objectid import ObjectId

from hanabiapi.api import rest
from hanabiapi import exceptions
from hanabiapi.datastores.dao import MetaGameDAO
from hanabiapi.utils.database import remove_object_ids_from_dict
from hanabiapi.datastores.mongo import utils

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

    @utils.check_object_id(_type='meta game')
    def read(self, _id=None):
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
        lookup_owner = {
            '$lookup': {
                'from': 'users',
                'localField': 'owner',
                'foreignField': '_id',
                'as': 'owner'
            }
        }
        lookup_players = {
            '$lookup': {
                'from': 'users',
                'localField': 'players',
                'foreignField': '_id',
                'as': 'players'
            }
        }
        match = {
            '$match': {
                '_id': ObjectId(_id),
            }
        }
        pipelines = [lookup_owner, lookup_players]
        if _id is not None:
            metagames = rest.database.db.metagames.find_one({'_id': ObjectId(_id)})
            if metagames is None:
                raise exceptions.MetaGameNotFound()
            pipelines.append(match)
        games = []
        for game in rest.database.db.metagames.aggregate(pipelines):
            game = remove_object_ids_from_dict(game)
            game['owner'] = game['owner'][0]
            games.append(game)

        if _id is not None:
            return games[0]
        return games

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

    @utils.check_object_id('meta game')
    def update(self, _id, meta_game):
        """
        Update a meta game.

        :param id: The id of the meta game to update.
        :param game: A dictionary representation of a meta game.
        :returns: None.
        """
        raise NotImplementedError

    @utils.check_object_id('meta game')
    def delete(self, _id=None, match=None):
        """
        Delete a meta game.

        If id is None delete all meta games.

        :param id: The id of the meta game to delete.
        :param match: A dictionary with which to delete metagames.
            Deletes them by matching the keys with values that exist
            in all metagames.
        :returns: None.
        """
        if _id is None and match is None:
            rest.database.db.metagames.remove()
        elif _id is not None:
            rest.database.db.metagames.remove({'_id': ObjectId(_id)})
        else:
            rest.database.db.metagames.remove(match)
