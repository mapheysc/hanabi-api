"""Defines objects to be used for interacting with users from a Mongo database."""
import logging
from bson.objectid import ObjectId

from hanabiapi.api import rest
from hanabiapi.exceptions import UserNotFound
from hanabiapi.datastores.dao import UserDAO

from hanabiapi.utils.database import remove_object_ids_from_dict

LOGGER = logging.getLogger(__name__)


class MongoUserDAO(UserDAO):
    """DAO responsible for interacting with users in Mongo."""

    def __init__(self):
        """Initialize the ``UserDAO`` object."""

    def search(self, **kwargs):
        """
        Search for users.

        :param kwargs: Keyword arguments to specify how to search.
        :returns: A list of users that match to search criteria.
        """
        users = []
        for user in rest.database.db.users.find(kwargs):
            users.append(remove_object_ids_from_dict(user))
        return users

    def read(self, _id=None):
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
        LOGGER.debug('Reading user data.')
        if _id is None:
            raise NotImplementedError
        else:
            user = rest.database.db.users.find_one({'_id': ObjectId(_id)})

            if user is None:
                raise UserNotFound

            return user

    def create(self, game):
        """
        Create a new user.

        :param user: A dictionary representation of a user.
        :returns: The id of the newly created user.
        """
        raise NotImplementedError

    def update(self, _id, user=None, as_model=False):
        """
        Update a user.

        :param id: The id of the user to update.
        :param user: A dictionary representation of a user.
        :param as_model: A ``UserModel`` representation of a user.
        :returns: None.
        """
        self.read(_id=_id)

        if as_model and user is not None:
            raise AttributeError('Cannot specify both user and as_model.')
        elif as_model:
            return UserModel(_id, user)
        else:
            # Remove _id because mongo doesn't like
            user = {k: v for k, v in user.items() if k != '_id'}
            rest.database.db.users.update({'_id': ObjectId(_id)}, user)

    def delete(self, id=None):
        """
        Delete a user.

        If id is None delete all users.

        :param id: The id of the user to delete.
        :returns: None.
        """
        raise NotImplementedError


class UserModel:
    """Model for interacting with a user."""

    def __init__(self, _id, user=None):
        """Initialize a ``UserModel``."""
        self._id = _id
        self.user = user

    def owns(self, own_data):
        """Update the owns data."""
        rest.database.db.users.update({'_id': ObjectId(self._id)}, {
            '$addToSet': {
                'owns': own_data
            }
        }, upsert=False)
