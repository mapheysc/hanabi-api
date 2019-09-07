"""Miscellaneous file utility functions."""

import logging
import os
import errno

LOGGER = logging.getLogger(__name__)


def create_file(path):
    """
    Check if a file exists.

    If it does not, creates an empty file with the given path. Will create directories that don't
    exist in the path.

    :param path: The path to create.
    :raises OSError: This shouldn't happen, but unexpected OSErrors will get raised (we catch
        EEXist already).
    :returns: ``None``.
    """
    LOGGER.debug('Creating new file: {}'.format(path))
    if not os.path.exists(path):
        # Make directory
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as err:
            if err.errno == errno.EEXIST:
                msg = ('Directory already created, or race condition? Check '
                       'path: {}'.format(path))
                LOGGER.error(msg)
            else:
                msg = 'Unexpected OSError: {}'.format(err)
                LOGGER.error(msg)
                raise OSError(msg)
        # Make file
        with open(path, 'a+') as f:
            f.close()
