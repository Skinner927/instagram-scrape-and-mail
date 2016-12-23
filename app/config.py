import tempfile
import json
import logging
from structs import *

# Defaults. Will get updated by the loaded config file.
config = {
    'settings': {
        'working_dir': tempfile.gettempdir(),
        'db': 'app.db',
        'log_level': 'warning',
        'max_media_count': 10,
    }
    # 'account': {
    #     'username': 'foobar',
    #     'password': 'hunter2'
    # },
    # Mail is optional. If not configured, no mail will be sent.
    # "mail": {
    #     "to": "foobar@mynixplay.com",
    #     "from": "robot@example.com",
    #     "smtp": {
    #         "server": "smtp.example.com",
    #         "username": "robot@example.com",
    #         "password": "hunter2"
    #     }
    # },
    # 'friends': {
    #     'joebob': {},
    #     'privateprincess': {
    #       'whitelist': ['onlyframe']
    #     }
    #   }
}


def parse_config(config_file_path):
    logger = logging.getLogger()  # Root Logger
    # Read config
    try:
        with open(config_file_path) as json_file:
            deep_update(config, json.load(json_file))

        settings = config.get('settings', {})
        # Log level
        log_lvl = settings.get('log_level', ' ')
        lvl = log_lvl.lower()[0]
        if lvl == 'c':
            logger.setLevel(logging.CRITICAL)
        elif lvl == 'e':
            logger.setLevel(logging.ERROR)
        elif lvl == 'w':
            logger.setLevel(logging.WARN)
        elif lvl == 'i':
            logger.setLevel(logging.INFO)
        elif lvl == 'd':
            logger.setLevel(logging.DEBUG)

        # "Verify" user & pass
        account = config.get('account')
        if (not account or 'username' not in account or
                    'password' not in account):
            msg = 'No username and/or password defined'
            logger.error(msg)
            raise LookupError(msg)

        # Ensure friends
        friends = config.get('friends')
        if type(friends) is not dict or len(friends.keys()) == 0:
            msg = 'No friends defined'
            logger.error(msg)
            raise LookupError(msg)

    except IOError as e:
        logger.critical('Cannot open config file.')
        logger.exception(e)
        raise e
