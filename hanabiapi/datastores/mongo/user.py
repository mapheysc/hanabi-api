"""Defines objects to be used for interacting with users from a Mongo database."""
import logging
from bson.objectid import ObjectId

from hanabiapi.api import rest

from hanabiapi.datastores.dao import UserDAO

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
        raise NotImplementedError

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

    def create(self, game):
        """
        Create a new user.

        :param user: A dictionary representation of a user.
        :returns: The id of the newly created user.
        """
        raise NotImplementedError

    def update(self, _id, user=None):
        """
        Update a user.

        :param id: The id of the user to update.
        :param user: A ``UserModel``.
        :returns: None.
        """
        return UserModel(_id, user)

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
