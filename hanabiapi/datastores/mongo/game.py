"""Defines objects to be used for interacting with games from a Mongo database."""
import logging
from bson.objectid import ObjectId

from hanabiapi.api import rest
import hanabiapi.exceptions as exceptions
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
                raise exceptions.GameNotFound

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

        try:
            self.user_dao.update(
                _id=user, as_model=True).owns(
                    own_data={'game': ObjectId(_id), 'player_id': 0})
        except exceptions.UserNotFound as unf:
            LOGGER.debug("User could not be found. Deleting the game.")
            self.delete(user, _id=_id)
            raise unf

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

    def delete(self, user, _id=None, match=None):
        """
        Delete a game.

        If id is None delete all games.

        :param user: The user who deleted the game.
        :param id: The id of the game to delete.
        :param match: A dictionary with which to delete games.
            Deletes them by matching the keys with values that exist
            in all games.
        :returns: None.
        """
        if _id is None and match is None:

            LOGGER.debug('Removing all games and metagames.')
            for user in self.user_dao.search():
                for i, game in enumerate(user['owns']):
                    del user['owns'][i]
                user = {k: v for k, v in user.items() if k != '_id'}
                self.user_dao.update(user['_id'], user)
            self.meta_game_dao.delete()
            rest.database.db.games.remove()

        elif _id is not None:

            LOGGER.debug(f'Removing games and metagames with id and game_id of {_id}.')
            for user in self.user_dao.search(**{'owns.game': ObjectId(_id)}):
                print(user)
                for i, game in enumerate(user['owns']):
                    if game['game'] == _id:
                        del user['owns'][i]
                self.user_dao.update(user['_id'], user)
            self.meta_game_dao.delete(match={'game_id': ObjectId(_id)})
            rest.database.db.games.remove({'_id': ObjectId(_id)})

        else:

            rest.database.db.games.remove(match)
            # TODO: Implement removing users data as well if game is removed.
