import logging
from datetime import datetime
import os

from instagram_scraper import InstagramScraper
import db
from config import config, parse_config
from structs import UserPrefs
from models import *
from file import mkdirs
from mail import mail_images


def run():
    logger = logging.getLogger(__name__)
    logger.info('Downloading files to: %s' % config['settings']['working_dir'])

    logger.debug('Creating database')
    db.get_session()

    logger.debug('Creating scraper')
    scraper = InstagramScraper(
        config['account']['username'],
        config['account']['password'])

    logger.debug('Scraper logging in')
    scraper.login()

    for username in config['friends']:
        user_prefs = UserPrefs(config['friends'][username])
        logger.info('Starting Instagram scrape for %s.' % username)
        ig_user = db.get_or_create_ig_user(username)

        # Attempt to initialize user if not already
        if not ig_user.initialized:
            profile = scraper.fetch_user(username)
            if not profile:
                logger.warn('Cannot find user profile: %s' % username)
            else:
                ig_user.full_name = profile['full_name']
                ig_user.profile_picture_url = profile['profile_pic_url']
                db.commit()

        _scrape_ig_and_mail_user_media(ig_user, user_prefs, scraper)

    logger.info('Complete.')


def _scrape_ig_and_mail_user_media(user, user_prefs, scraper):
    logger = logging.getLogger(__name__)
    logger.debug('Scraping Instagram for %s' % user.username)

    download_dir = os.path.abspath(config['settings']['working_dir'])
    mkdirs(download_dir)

    # Loop over all media
    new_media = []
    for media in scraper.media_gen(user.username, max_count=config[
        'settings']['max_media_count']):

        ig_media = db.create_ig_media_if_not_exist(media, user)

        if not ig_media:
            continue

        logger.info('Created new media entry: %s %s' % (
            ig_media.type, ig_media.url))

        new_media.append(ig_media)

        try:
            if ig_media.type == MediaTypeEnum.image:
                filename = '_'.join([
                    'ig',
                    user.username,
                    media['created_time'] or str(datetime.utcnow())])
                f_with_ext = scraper.download(media, download_dir, filename)
                if f_with_ext:
                    # Returns false if file already exists
                    ig_media.last_downloaded = datetime.utcnow()
                    ig_media.file_path = f_with_ext
            else:
                # Disable video for the moment
                ig_media.enabled = False
        except Exception as e:
            logger.error('Error downloading media')
            logger.exception(e)

    logger.info('%s new images.' % len(
        [m for m in new_media if m.type == MediaTypeEnum.image]))
    logger.info('%s new videos.' % len(
        [m for m in new_media if m.type == MediaTypeEnum.video]))
    if len(new_media) == 0:
        return

    # Save to db
    session = db.get_session()
    for media in new_media:
        session.add(media)
    session.commit()

    # Send images via mail
    if 'mail' not in config:
        logger.debug('Not sending mail, no mail configured')
        return
    files = [os.path.join(download_dir, m.file_path) for m in new_media if
             m.type == MediaTypeEnum.image]
    logger.debug('Mailing %s files:' % len(files))
    logger.debug('\n'.join(files))
    mail_images(files)
