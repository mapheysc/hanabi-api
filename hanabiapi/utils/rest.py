"""A collection of REST related utility functions."""
import logging
from flask_restplus import abort
from flask import request
from werkzeug import exceptions

LOGGER = logging.getLogger(__name__)


def get_body(is_required=True):
    """
    Get body of a request, checking first if body is missing.

    This method should be called when handling requests that should have a body.

    :param is_required: If True, will raise an error on a bad/missing body. If False, return
        ``None`` on a bad/missing body.
    :raises werkzeug.exceptions.BadRequest: If given a request with no body or the body is
        not valid JSON, and abort with a ``400`` status code if ``is_required`` is True.
    :returns: If ``request.get_data()`` exists and is valid JSON, return it as JSON. ``None``
        otherwise.
    """
    LOGGER.debug('Checking if body exists.')
    if not request.get_data():
        msg = (f'The {request.endpoint} endpoint {request.method} method requires a body in the '
               'request.')
        LOGGER.debug(msg)
        if is_required:
            return abort(400, msg)
    LOGGER.debug(f'Body exists for request {request}. Attempting to return as JSON.')
    try:
        return request.get_json(force=True)
    except exceptions.BadRequest:
        msg = ('The request contained a body but the body was not valid JSON. Body given: '
               f'{request.data}')
        LOGGER.debug(msg)
        if is_required:
            return abort(400, msg)


def check_keys(required_keys=None, optional_keys=None, check_request_body=False):
    """
    Log any unexpected keys. Fail if necessary keys are missing.

    :param required_keys: Optional. A list of required keys as dicts. Each dict must have a
                          key and type field where the key is the name of the required key
                          as a string and the type is the type of the key as a string. If any keys
                          are missing in the request, abort.
    :param optional_keys: Optional. A list of optional keys as dicts. Each dict must have a
                          key and type field where the key is the name of the required key
                          as a string and the type is the type of the key as a string.
    :param check_request_body: Optional. If set to True check the keys only in
                               the body of the request.
    :returns: None if required keys are present and non-empty. 400 if missing a
              required key or required key is an empty string.
    """
    if required_keys is None:
        required_keys = []
    if optional_keys is None:
        optional_keys = []

    valid_keys = required_keys + optional_keys

    if check_request_body:
        args_dict = get_body(is_required=True)
    else:
        args_dict = request.args.to_dict()

    for key in optional_keys:
        optional_key = key.get('key')
        optional_type = key.get('type')
        if optional_key is None:
            raise AttributeError(f'Missing field "key" in {key}')
        if optional_type is None:
            raise AttributeError(f'Missing field "type" in {key}')
        if args_dict.get(optional_key) is not None:
            if str(type(args_dict[optional_key])) != optional_type:
                msg = f'Optional key {optional_key} given as {type(args_dict[optional_key])}.' \
                    f' Expected {optional_type}'
                LOGGER.debug(msg)
                return abort(400, msg)

    for key in required_keys:
        required_key = key.get('key')
        required_type = key.get('type')
        if required_key is None:
            raise AttributeError(f'Missing field "key" in {key}')
        if required_type is None:
            raise AttributeError(f'Missing field "type" in {key}')
        if required_key not in args_dict:
            msg = f'Missing required arg: {required_key}'
            LOGGER.debug(msg)
            return abort(400, msg)
        if str(type(args_dict[required_key])) != required_type:
            msg = f'Required key {required_key} given as {type(args_dict[required_key])}.' \
                f' Expected {required_type}'
            LOGGER.debug(msg)
            return abort(400, msg)
        if not args_dict[required_key]:
            msg = f'Required arg: {required_key} cannot be empty string.'
            LOGGER.debug(msg)
            return abort(400, msg)

    # Log any additional unexpected keys
    for key, value in args_dict.items():
        if key not in [k['key'] for k in valid_keys]:
            msg = f'Query received unexpected parameter, {key}: {value}'
            LOGGER.debug(msg)
