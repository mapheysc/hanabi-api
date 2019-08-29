"""Define user package requirements and various project metadata."""

from setuptools import setup, find_packages

VERSION = __import__('api').__VERSION__

setup(name='Hanabi',
      version=VERSION,
      author='Sam Maphey',
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'hanabi = launcher:main',
        ]
      },
      install_requires=[
        'flask',
        'flask-jwt-extended',
        'flask-cors',
        'gunicorn',
        'requests',
        'pyyaml',
        'ldap3',
        'flask-socketio',
        'eventlet',
      ],
      extras_require={
        'flask_cors': [
            'flask-cors',
        ],
        'cert_checker': [
            'cryptography',
        ],
      },
      )
