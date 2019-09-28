"""Utility functions for mongo database."""
import functools
from bson.objectid import ObjectId
from bson.errors import InvalidId

from hanabiapi import exceptions
from hanabiapi.datastores.dao import UtilsDAO


def check_object_id(_type):
    """Check that the given object id is a valid bson ObjectId."""
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                try:
                    _id = kwargs['_id']
                except KeyError:
                    # _id must be args[1]
                    if len(args) > 1:
                        _id = args[1]
                    else:
                        # There is no id
                        return view_func(*args, **kwargs)
                ObjectId(_id)
            except InvalidId:
                raise exceptions.NotFound(_type=_type)
            return view_func(*args, **kwargs)
        return wrapper
    return decorator


class MongoUtilsDAO(UtilsDAO):
    """The DAO responseible for handling utility functions in Mongo."""

    def populate(obj):
        """Replace any reference field with a json representation."""
        for key, value in obj:
            print(key, value)
        return obj
