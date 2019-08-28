"""Defines the version of DarcPy."""

import logging
import subprocess
import os

LOGGER = logging.getLogger(__name__)

__VERSION__ = "19.08.0"


def get_version():
    """
    Get the version of the package.

    If this is called inside of a git repository and is on a branch other than master, it will
    attach the current working branch after the version. For example, if I was on a branch called
    ``my-feature-branch`` and my version currently read ``19.08.0``, it would print
    ``19.08.0 (my-feature-branch)``.

    :returns: The version of DarcPy.
    """
    LOGGER.debug('Grabbing version: {}'.format(__VERSION__))
    branch_name = None
    try:
        branch_process = subprocess.Popen(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=os.path.dirname(os.path.realpath(__file__)),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        branch_out, branch_err = branch_process.communicate()
        branch_name = branch_out.strip().decode('utf-8')

    except subprocess.CalledProcessError:
        LOGGER.debug('Outside of a git repo. Not appending branch name to '
                     'version.')
    except FileNotFoundError:
        LOGGER.debug(
            'git is not installed. Not appending branch name to version.'
        )
    if branch_name and branch_name != 'master':
        return __VERSION__ + ' (' + branch_name + ')'
    return __VERSION__
