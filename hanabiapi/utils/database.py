"""Defines utils functions for common database operations."""

import logging
from bson.objectid import ObjectId
from pymongo import MongoClient

from hanabiapi.api.config.config import Config

LOGGER = logging.getLogger(__name__)
CONFIG = Config()


class Database:
    """Create an instance of the database."""

    def __init__(self):
        """Initialize a Database instance."""
        # self.client = {'hanabi': None}
        # self.db = self.client['hanabi']
        LOGGER.debug(f'Creating database')
        DATABASE_CONFIG = CONFIG['database']
        auth = {}
        LOGGER.debug(f'Setting up authentication')
        try:
            auth = {
                'username': DATABASE_CONFIG['username'],
                'password': DATABASE_CONFIG['password'],
                'authSource': DATABASE_CONFIG['auth']
            }
            LOGGER.debug(f'Using authentication')
        except KeyError:
            # Not using authentication
            LOGGER.debug(f'No authentication')
            pass
        self.client = MongoClient(DATABASE_CONFIG['url'], **auth)
        LOGGER.debug(f'Creating client')
        self.db = self.client.hanabi
        LOGGER.debug(f'Created Mongo connection')


def remove_object_ids_from_dict(di):
    """Replace all bson ObjectIds with strings."""
    for k, v in di.items():
        if isinstance(v, dict):
            remove_object_ids_from_dict(v)
        elif isinstance(v, list):
            remove_object_ids_from_list(v)
        else:
            if isinstance(v, ObjectId):
                di[k] = str(v)
    return di


def remove_object_ids_from_list(li):
    """Replace all bson ObjectIds with strings."""
    for i, v in enumerate(li):
        if isinstance(v, dict):
            remove_object_ids_from_dict(v)
        elif isinstance(v, list):
            remove_object_ids_from_list(v)
        else:
            if isinstance(v, ObjectId):
                li[i] = str(v)
    return li
