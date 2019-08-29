# Hanabi API

## Building the API locally

- clone the repo
- clone the hanabi-engine repo

## Documentation

[Developer docs (not hosted yet)](google.com)

[API docs (not hosted yet)](google.com)

## Install Requirements

**Build a vitrual environment if you wish (highly reccommended)**
`python -m venv hanabi`

Install mongodb

`brew install mongo`

Start mongodb service

`mongod`

`cd hanabi-api && pip install -r requirements.txt`

`cd hanabi-engine && pip install -r requirements.txt`

## Run the local flask app

`cd hanabi-api && hanabi -s -l DEBUG`

**Enjoy!**
