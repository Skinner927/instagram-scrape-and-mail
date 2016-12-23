from smtplib import SMTP_SSL
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
import logging
import math

from config import config

MAX_IMG_PER_EMAIL = 10


def _chunky(files, n):
    for i in xrange(0, len(files), n):
        yield files[i:i + n]


def mail_images(file_paths):
    logger = logging.getLogger(__name__)
    conn = SMTP_SSL(config['mail']['smtp']['server'])
    conn.set_debuglevel(False)
    try:
        conn.login(config['mail']['smtp']['username'],
                   config['mail']['smtp']['password'])
        logger.debug('connected to SMTP server')
        logger.debug('%d images to be sent via %d emails' % (
            len(file_paths),
            math.ceil(len(file_paths) / float(MAX_IMG_PER_EMAIL))))

        email_count = 1
        # Chunk the files up by MAX_IMG_PER_EMAIL to limit size.
        for file_group in _chunky(file_paths, MAX_IMG_PER_EMAIL):
            msg = MIMEMultipart()
            msg['From'] = config['mail']['from']
            msg['To'] = config['mail']['to']
            msg['Date'] = formatdate(localtime=True)

            for f in file_group:
                try:
                    with open(f, 'rb') as fil:
                        part = MIMEApplication(
                            fil.read(),
                            Name=basename(f)
                        )
                        part['Content-Disposition'] = \
                            'attachment; filename="%s"' % basename(f)
                        msg.attach(part)
                except IOError:
                    logger.error('Cannot read file: %s' % f)
                    # Can't read the image, next
                    continue

            conn.sendmail(msg['From'], msg['To'], msg.as_string())
            logger.debug('Sending email %s' % email_count)
            email_count += 1
    finally:
        conn.quit()
