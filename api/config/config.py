"""Used for holding configuration for DarcPy."""
import os
import logging

import yaml

LOGGER = logging.getLogger(__name__)
CONFIG_LOCATION = 'config.yml'


class Config(object):
    """
    Python representation of the config.yml file.

    Here is an example config.yml file:

        .. code-block:: yaml

            flask:
                JWT_ACCESS_TOKEN_EXPIRES_HOURS: 12
                secret: this_is_a_fake_secret
            app:
                ip: https://darc-dev.llnl.gov
                email: mdm@llnl.gov
            ldap:
                host: the-lab.llnl.gov
                port: 636
                domain_name: '@the-lab.llnl.gov'
            marklogic:
                manage_port: 8002
                rest_port: 8047
                username: admin
                password: admin
                userpassword: user
    """

    def __init__(self, config_file=None):
        """Initialize the ``Config`` object."""
        self.config_file = config_file
        self.config = {}
        if not self.config_file:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            self.config_file = os.path.join(dir_path, CONFIG_LOCATION)
        try:
            self.config = yaml.safe_load(open(self.config_file))
        except FileNotFoundError:
            # Grab sample file IF I GOT HERE THIS IS NOT GOOD
            dir_path = os.path.dirname(os.path.realpath(__file__))
            self.config_file = os.path.join(dir_path, 'config-sample.yml')
            self.config = yaml.safe_load(open(self.config_file))
            LOGGER.critical('Missing config file at: {}'
                            .format(self.config_file))

    # The following methods are to make the Config class object subscriptable.
    # This allows you to access config attributes like this:
    #       C = Config()
    #       C['app']['ip']
    # Instead of having to do this:
    #       C.config['app']['ip']
    def __getitem__(self, key):
        """
        Get the entry in the ``Config`` object with the given key.

        :param: The key to the entry to get.
        :returns: The entry of the given key.
        """
        return self.config[key]

    def __setitem__(self, key, value):
        """
        Set the entry in this ``Config`` object with the given key.

        :param key: The key to set.
        :param value: The value to set.
        """
        self.config[key] = value

    def __delitem__(self, key):
        """
        Delete the entry in this ``Config`` object with the given key.

        :param key: The key of the key-value pair to delete.
        """
        del self.config[key]

    def __repr__(self):
        """
        Return the string representation of a ``Config`` object.

        Currently only prints out the config file location.

        For example -

        ``'Config <config_file=/Users/eklund7/projects/dlm/darc/python/darcpy/config/config.yml'``

        :returns: The string representation of a ``Config`` object.
        """
        return ('Config <config_file={}>'.format(self.config_file))
