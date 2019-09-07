"""Defines objects to be used for interacting with games from a Mongo database."""
import logging
from bson.objectid import ObjectId

from hanabiapi.api import rest
from hanabiapi.exceptions import GameNotFound
from hanabiapi.datastores.dao import GameDAO
from hanabiapi.datastores.mongo.user import MongoUserDAO
from hanabiapi.datastores.mongo.metagame import MongoMetaGameDAO

LOGGER = logging.getLogger(__name__)


class MongoGameDAO(GameDAO):
    """DAO responsible for interacting with games in Mongo."""

    def __init__(self):
        """Initialize the ``MongoGameDAO`` object."""
        self.user_dao = MongoUserDAO()
        self.meta_game_dao = MongoMetaGameDAO()

    def search(self, **kwargs):
        """
        Search for games.

        :param kwargs: Keyword arguments to specify how to search.
        :returns: A list of games that match to search criteria.
        """
        raise NotImplementedError

    def read(self, _id=None):
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
        LOGGER.debug('Reading game data.')
        if _id is None:
            return [
                {
                    'name': game['name'],
                    'id': str(game['_id'])
                } for game in rest.database.db.games.find()
            ]
        else:
            game = rest.database.db.games.find_one({'_id': ObjectId(_id)})

            if game is None:
                raise GameNotFound

            return game

    def create(self, user, game):
        """
        Create a new game.

        :param user: The user who created the game.
        :param game: A dictionary representation of a game
            built from the hanabi game engine.
        :returns: The id of the newly created game.
        """
        _id = rest.database.db.games.insert_one(game).inserted_id

        LOGGER.debug("Adding game to users list of owned games.")
        self.user_dao.update(user).owns(own_data={'game': ObjectId(_id), 'player_id': 0})

        LOGGER.debug("Creating meta game reference.")
        self.meta_game_dao.create({
            'game_id': _id,
            'turn': game['turn'],
            'game_name': game['name'],
            'num_hints': game['num_hints'],
            'num_errors': game['num_errors'],
            'owner': user,
            'num_players': len(game['players']),
            'players': [user]
        })

        return str(_id)

    def update(self, id, game):
        """
        Update a game.

        :param id: The id of the game to update.
        :param game: A dictionary representation of a game
            built from the hanabi game engine.
        :returns: None.
        """
        raise NotImplementedError

    def delete(self, user, id=None):
        """
        Delete a game.

        If id is None delete all games.

        :param user: The user who deleted the game.
        :param id: The id of the game to delete.
        :returns: None.
        """
        raise NotImplementedError
