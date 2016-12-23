import logging
import requests
import json
import re
import os
import time

"""
Copied from https://github.com/rarcega/instagram-scraper and tweaked to fit
our specific needs.
"""

# Stolen from
# PD License
BASE_URL = 'https://www.instagram.com/'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
LOGOUT_URL = BASE_URL + 'accounts/logout/'
MEDIA_URL = BASE_URL + '{0}/media'

STORIES_URL = 'https://i.instagram.com/api/v1/feed/user/{0}/reel_media/'
STORIES_UA = 'Instagram 9.5.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+'
STORIES_COOKIE = 'ds_user_id={0}; sessionid={1};'


class InstagramScraper(object):
    """
    Non-API tool to strip images from Instagram users.
    I tried the IG API. It's neat to get instant notifications of new images,
    but I personally don't think it is worth the hassle.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.logger = logging.getLogger(__name__)

        self.session = requests.Session()
        self.cookies = None

        # if self.username and self.password:
        #     self.login()

    @property
    def logged_in(self):
        # TODO: Implement caching, to only check after X amount of time.
        if not self.session:
            return False
        me = self.fetch_user(self.username)
        if me is not None:
            return True
        return False

    def login(self):
        """Logs in to instagram"""
        self.session.headers.update({'Referer': BASE_URL})
        req = self.session.get(BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

        login_data = {'username': self.username, 'password': self.password}
        login = self.session.post(LOGIN_URL, data=login_data,
                                  allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.cookies = login.cookies

        if login.status_code == 200 and json.loads(login.text)['authenticated']:
            # self.logged_in = True
            pass
        else:
            self.logger.exception('Login failed for ' + self.username)
            raise ValueError('Login failed for ' + self.username)

    def logout(self):
        """Logs out of instagram"""
        if self.logged_in:
            try:
                logout_data = {'csrfmiddlewaretoken': self.cookies['csrftoken']}
                self.session.post(LOGOUT_URL, data=logout_data)
                # self.logged_in = False
                self.session = None
            except requests.exceptions.RequestException:
                self.logger.warning('Failed to log out ' + self.username)

    def media_gen(self, username, min_id=None, max_id=None, max_count=10):
        """
        Generator of all user's media
        :param str username: Username to pull media from
        :param str min_id: (Optional) Pagination start
        :param str max_id: (Optional) Pagination end
        :param int max_count: (Optional, default=10) Max number of media to
            return.
        :returns dict: JSON dictionary representing a media query.
        """
        count = 0
        try:
            media = self.fetch_media_json(username, min_id=min_id,
                                          max_id=max_id)

            while True:
                for item in media['items']:
                    if count >= max_count:
                        return
                    count += 1
                    yield item

                if media.get('more_available'):
                    max_id = media['items'][-1]['id']
                    media = self.fetch_media_json(username, max_id=max_id)
                else:
                    return
        except ValueError:
            self.logger.exception('Failed to get media for ' + username)

    def fetch_media_json(self, username, min_id=None, max_id=None):
        """Fetches the user's media metadata"""
        url = MEDIA_URL.format(username) + '?'

        if min_id is not None:
            url += '&min_id=' + min_id
        if max_id is not None:
            url += '&max_id=' + max_id

        resp = self.session.get(url)

        if resp.status_code == 200:
            media = json.loads(resp.text)

            if not media['items']:
                raise ValueError('User {0} is private'.format(username))

            media['items'] = [self.set_media_url(item) for item in
                              media['items']]
            return media
        else:
            raise ValueError('User {0} does not exist'.format(username))

    def fetch_user(self, username):
        """Fetches the user's metadata"""
        resp = self.session.get(BASE_URL + username)

        if resp.status_code == 200 and '_sharedData' in resp.text:
            shared_data = \
                resp.text.split("window._sharedData = ")[1].split(";</script>")[
                    0]
            return json.loads(shared_data)['entry_data']['ProfilePage'][0][
                'user']

    def fetch_stories(self, user_id):
        """Fetches the user's stories"""
        # user_id == user['id']
        resp = self.session.get(STORIES_URL.format(user_id), headers={
            'user-agent': STORIES_UA,
            'cookie': STORIES_COOKIE.format(self.cookies['ds_user_id'],
                                            self.cookies['sessionid'])
        })

        retval = json.loads(resp.text)

        if resp.status_code == 200 and 'items' in retval and len(
                retval['items']) > 0:
            return [self.set_story_url(item) for item in retval['items']]
        return []

    def download(self, item, save_dir='./', filename=None):
        """
        Downloads the media file
        :param dict item: JSON item returned from `fetch_media_json()`
        :param str save_dir: Optional directory to save download in. Defaults to
            current directory.
        :param str filename: Optional filename without extension, defaults to
            Instagram's filename.
        :returns str: the filename the media was saved as.
        """
        base_name = item['url'].split('/')[-1]
        if filename is not None:
            extension = base_name.split('.')[-1]
            base_name = filename + '.' + extension

        file_path = os.path.join(save_dir, base_name)

        with open(file_path, 'wb') as media_file:
            try:
                content = self.session.get(item['url']).content
            except requests.exceptions.ConnectionError:
                time.sleep(5)
                content = requests.get(item['url']).content

            media_file.write(content)

        file_time = int(
            item.get('created_time', item.get('taken_at', time.time())))
        os.utime(file_path, (file_time, file_time))
        return base_name

    @staticmethod
    def set_media_url(item):
        """Sets the media url"""
        item['url'] = \
            item[item['type'] + 's']['standard_resolution']['url'].split('?')[0]
        # remove dimensions to get largest image
        item['url'] = re.sub(r'/s\d{3,}x\d{3,}/', '/', item['url'])
        return item

    @staticmethod
    def set_story_url(item):
        """Sets the story url"""
        item['url'] = \
            item['image_versions2']['candidates'][0]['url'].split('?')[0]
        return item
