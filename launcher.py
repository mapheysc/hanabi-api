"""Setup CLI and logging."""

import logging
import inspect
import os
import flask_cors

from argparse import ArgumentParser, RawTextHelpFormatter

import api.rest as rest
from utils.files import create_file

ROOTLOGGER = logging.getLogger(inspect.getmodule(__name__))
LOGGER = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s - %(name)s:%(funcName)s:%(lineno)s - " \
             "%(levelname)s - %(message)s"
DEFAULT_LOG_PATH = os.path.join(os.path.expanduser('~'), '.hanabi/hanabi.log')
DEFAULT_LOG_LEVEL = 'WARNING'

__VERSION__ = __import__('api').get_version()


def setup_arg_parser():
    """
    Set up the argument parser.

    :returns: An ``ArgumentParser`` object.
    """
    parser = ArgumentParser(prog='hanabi',
                            description='A Flask based controller that defines'
                            ' a RESTful interface to play hanabi.',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='store_true',
                        help="display version information and exit.")
    parser.add_argument('-s', '--stdout', action='store_true',
                        help='display logs to stdout.')
    parser.add_argument('-l', '--loglevel', help='What level to log at.',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO',
                                 'DEBUG'])
    parser.add_argument('-p', '--logpath', help='Where to put the log file.')
    return parser


def setup_logging(args):
    """
    Set up logging based on provided log params.

    :param args: (ArgumentParser, req) Command line args that tell us how to set up logging. If
        not provided, use some defaults.
    """
    if args.logpath:
        logpath = args.logpath
    else:
        logpath = DEFAULT_LOG_PATH
    if args.loglevel:
        loglevel = args.loglevel
    else:
        loglevel = DEFAULT_LOG_LEVEL

    create_file(logpath)

    formatter = logging.Formatter(LOG_FORMAT)
    ROOTLOGGER.setLevel(loglevel)

    # Setup file handler
    fh = logging.FileHandler(logpath)
    fh.setLevel(loglevel)
    fh.setFormatter(formatter)
    ROOTLOGGER.addHandler(fh)

    if args.stdout:
        # Add the StreamHandler
        sh = logging.StreamHandler()
        sh.setLevel(loglevel)
        sh.setFormatter(formatter)
        ROOTLOGGER.addHandler(sh)

    LOGGER.info("-------------------------STARTING-------------------------")
    LOGGER.info("INFO Logging Level -- Enabled")
    LOGGER.warning("WARNING Logging Level -- Enabled")
    LOGGER.critical("CRITICAL Logging Level -- Enabled")
    LOGGER.debug("DEBUG Logging Level -- Enabled")


def version():
    """
    Return the version of the package.

    :returns: The version of Hanabi.
    """
    LOGGER.debug('Getting version: {}.'.format(__VERSION__))
    return __VERSION__


def main():
    """
    Development entry point for DarcPy.

    Make calls to setup CLI arg parser, parse command line, and execute based on those args.

    **IMPORTANT NOTE**: This function should *only* be used for development purposes. For
    production, the DarcPy package should be paired with a real WSGI HTTP Server, such as
    `Gunicorn <https://gunicorn.org/>`_.
    """
    parser = setup_arg_parser()
    args = parser.parse_args()
    setup_logging(args)
    LOGGER.debug('Logging successfully setup.')
    if args.version:
        print(version())
    else:
        rest.socketio.run(rest.app, host='0.0.0.0', debug=True)


if __name__ == "__main__":
    main()

if __name__ != "__main__":
    # This section will pass the gunicorn loglevel down to flask when running via gunicorn
    gunicorn_logger = logging.getLogger("gunicorn.error")
    ROOTLOGGER.setLevel(gunicorn_logger.level)
    ROOTLOGGER.handlers = gunicorn_logger.handlers
