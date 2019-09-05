"""Defines utils functions for common database operations."""

from bson.objectid import ObjectId
from pymongo import MongoClient


class Database:
    """Create an instance of the database."""

    def __init__(self):
        """Initialize a Database instance."""
        self.client = MongoClient(host='localhost:27017')
        self.db = self.client.hanabi


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
