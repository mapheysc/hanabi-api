"""Create a haiku."""

import json
import random
import os
import logging

LOGGER = logging.getLogger(__name__)


def generate_haiku(haiku_file=None):
    """
    Generate a random haiku.

    :param haiku_file: The json file of haikus to load. Defaults to
        data/haikus.json.
    :returns: A dictionary containing the haiku.
    """
    if not haiku_file:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        haiku_file = os.path.join(dir_path, '../api/data/haikus.json')
    LOGGER.debug('Generating a haiku with file: {}.'.format(haiku_file))
    haiku = {}
    with open(haiku_file) as file:
        data = json.load(file)
    author_key = random.choice(list(data))
    haiku['author'] = data[author_key]['author']
    haiku['haiku'] = random.choice(data[author_key]['haikus'])
    return haiku
