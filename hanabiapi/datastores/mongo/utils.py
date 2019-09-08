"""Utility functions for mongo database."""
import functools
from bson.objectid import ObjectId
from bson.errors import InvalidId

from hanabiapi import exceptions


def check_object_id(_type):
    """Check that the given object id is a valid bson ObjectId."""
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                try:
                    _id = kwargs['_id']
                except KeyError:
                    # _id must be args[0]
                    _id = args[0]
                ObjectId(_id)
            except InvalidId:
                raise exceptions.NotFound(_type=_type)
            return view_func(*args, **kwargs)
        return wrapper
    return decorator
