"""Decorators used throughout Hanabi."""
import logging
import functools

from hanabiapi.utils import rest as rest_utils

LOGGER = logging.getLogger(__name__)


def check_keys(required_keys=None, optional_keys=None, check_request_body=False):
    """
    Add to methods to log any unexpected keys. Fail if necessary keys are missing.

    :param required_keys: A list of required keys as strings. If any keys are missing in the
        request, abort.
    :param optional_keys: A list of optional keys as strings.
    :param check_request_body: If set to ``True`` check the keys only in the body of the request.
    :returns: Either the function being decorated or a ``flask.Response`` object.

        - If successfully checked the keys:

            The function being decorated.

        - If missing a required key:

            A ``flask.Response`` object that contains the following:

                ``400`` status code and a body containing a message stating the required key is
                missing.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            rest_utils.check_keys(required_keys=required_keys,
                                  optional_keys=optional_keys,
                                  check_request_body=check_request_body)
            return view_func(*args, **kwargs)
        return wrapper
    return decorator
