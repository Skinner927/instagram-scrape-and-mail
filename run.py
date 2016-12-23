import logging
import argparse

import app
from app.config import config, parse_config
from app.db import close_database

logging.basicConfig()
logger = logging.getLogger()

parser = argparse.ArgumentParser(description='Ig Scrape and Mail')
parser.add_argument('config', default='config.json', nargs='?',
                    help='App config to use. (default:%(default)s)')
parser.add_argument('--max-media', default=None, metavar='N',
                    help='Override config max number of media to look at.')
parser.add_argument('--no-mail', action='store_true',
                    help='Do not send e-mail.')
parser.add_argument('--friends', nargs='*', default=[],
                    help='Override list of Instagram users to scrape')
parser.add_argument('--debug', action='store_true',
                    help='Set the log level to debug')

args = parser.parse_args()

try:
    logger.debug('Reading config')
    parse_config(args.config)

    # Overrides
    if args.max_media is not None:
        config['settings']['max_media_count'] = int(args.max_media)
    if args.no_mail and 'mail' in config:
        del config['mail']
    if len(args.friends) > 0:
        config['friends'] = {}
        for f in args.friends:
            config['friends'][f] = {}
    if args.debug:
        config['settings']['log_level'] = logging.DEBUG

    app.run()
finally:
    close_database()
