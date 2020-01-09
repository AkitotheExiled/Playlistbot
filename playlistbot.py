import praw
from configparser import ConfigParser
from datetime import datetime, timedelta
import requests, requests.auth
import time
import re
from data_func import dataFunc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchFrameException, WebDriverException



# Test cases for script
## Test if user pauses the video, determine how often to check and if video should be skipped or auto-played.
### test if user accidentally closes the video, should the script open up a new tab where the song left off?


class PlaylistBot():

    def __init__(self):
        self.user_agent = "PlaylistBot V0.5 BETA by ScoopJr"
        print('Starting up...', self.user_agent)
        CONFIG = ConfigParser()
        CONFIG.read('config.ini')
        self.user = CONFIG.get('main', 'USER')
        self.password = CONFIG.get('main', 'PASSWORD')
        self.client = CONFIG.get('main', 'CLIENT_ID')
        self.secret = CONFIG.get('main', 'SECRET')
        self.subreddit = CONFIG.get('main', 'SUBREDDIT')
        self.token_url = "https://www.reddit.com/api/v1/access_token"
        self.token = ""
        self.t_type = ""
        self.reddit = praw.Reddit(client_id=self.client,
                                  client_secret=self.secret,
                                  password=self.password,
                                  user_agent=self.user_agent,
                                  username=self.user)
        self.subs = {}
        self.urls = set()
        self.post_link_date = None
        self.now = datetime.now()
        try:
            with open('lastposttime.txt', 'r') as r:
                data = r.read()
                # time_data = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                # before_time = self.timedelta_to_largest_time(datetime.now()-time_data)
            self.before = data
            print('The last grabbed posts UTC timestamp is', self.before)
        except IOError:
            print('Could not read file: lastposttime.txt')
            self.before = 'Never.'
        if not self.before:
            self.before = 'Never.'
        # SELENIUM STUFF BABY
        try:
            self.driver = webdriver.Chrome('chromedriver.exe')
        except WebDriverException:
            print('MESSAGE: chromedriver.exe needs to be in the same folder as the script. Please contain playlistbot.py and chromedriver.exe in the same folder.')
            exit()
        self.last_post = None

    # REDDIT
    def get_token(self):
        client_auth = requests.auth.HTTPBasicAuth(self.client, self.secret)
        post_data = {'grant_type': 'password', 'username': self.user, 'password': self.password}
        headers = {'User-Agent': self.user_agent}
        response = requests.Session()
        response2 = response.post(self.token_url, auth=client_auth, data=post_data, headers=headers)
        if 'error' in response2.json().keys():
            return 400
        else:
            try:
                self.token = response2.json()['access_token']
                self.t_type = response2.json()['token_type']
                return 200
            except Exception as e:
                return print(e)

    def timedelta_to_largest_time(self, timedelta):
        print(timedelta)
        try:
            days = timedelta.days
            seconds = timedelta.seconds
            minutes = (timedelta.seconds // 60) % 60
            hours = int(timedelta.seconds // 3600)
            weeks = days * 7
        except AttributeError as e:
            print(e)
        if days <= 0:
            return str(hours) + 'h'
        else:
            return str(days) + 'd'

    def grab_urls(self, time='', before=''):
        """Grabs all posts for the subreddit and puts their created_utc, archived status, locked status into a dictionary self.subs categorized under their post.id"""

        subreddit = self.subreddit
        size = 500
        befor = before
        after = time
        if self.before != 'Never.':
            befor = self.before
            after = '1h'
        url = "https://api.pushshift.io/reddit/submission/search/?subreddit={}&size={}&before={}&after={}".format(
            subreddit, size, befor, after)
        response = requests.get(url).json()
        print(response)
        if response['data']:
            last_post_time = None
            final_post = None
            for item in response['data']:
                self.urls.add(item['url'])
                last_post_time = item['created_utc']
                pre_post_time = datetime.utcfromtimestamp(int(last_post_time)).strftime('%Y-%m-%d %H:%M:%S')
                post_time = datetime.strptime(pre_post_time, '%Y-%m-%d %H:%M:%S')
                final_post = last_post_time
            with open('lastposttime.txt', 'w+') as f:
                f.write(str(final_post))
            self.grab_urls(before=last_post_time)
        else:
            return list(self.urls)

    # PYTHON
    def sort_urls_by_domain(self, urls):
        """Takes a list of urls and sorts them by domain name and returns a dictionary"""
        try:
            urls2 = list(urls)
        except TypeError as e:
            return print(e)
        sc_list = []
        other_list = []
        youtube_list = []
        for url in urls2:
            if (('youtube' in url) or ('youtu.be' in url)) & ('reddit' not in url):
                youtube_list.append(url)
            if 'soundcloud' in url:
                sc_list.append(url)
            if 'youtube' not in url and 'soundcloud' not in url and 'youtu.be' not in url:
                other_list.append(url)
        return {'youtube': youtube_list, 'soundcloud': sc_list, 'other': other_list}

    def get_videoid_from_url(self, url):
        pattern = re.compile(r'^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*')
        result = re.search(pattern, url)
        return result.group(2)

    def play_song(self, low_v, high_v):
        db_func = dataFunc()
        urls = db_func.select_url_between_values(low_val=low_v, high_val=high_v)
        pos, act_urls = zip(*urls)
        for url in act_urls:
            self.driver.get(url)
            while True:
                skip_input = input('Do you want to skip this song?(type stop to redo track selection)')
                if str(skip_input) == 'stop':
                    return
                if 's' or 'y' in str(skip_input):
                    break
                player_state = self.driver.execute_script(
                    "return document.getElementById('movie_player').getPlayerState()")
                if player_state == 0:
                    self.driver.execute_script('document.getElementsByTagName("video")[0].pause()')
                    break
                if player_state == -1:
                    try:
                        self.driver.switch_to.frame(self.driver.find_element_by_id('player'))
                        WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Play"]'))).click()
                    except NoSuchFrameException:
                        print('The script could not find the video player.  An ad may be playing right now!')
                time.sleep(4)

    def normal_run(self):
        self.grab_urls()
        data = self.sort_urls_by_domain(list(self.urls))
        data_func = dataFunc()
        for url in data['youtube']:
            data_func.insert_into_table(pos=data['youtube'].index(url), url=url)


if __name__ == "__main__":
    bot = PlaylistBot()
    answ = input('First run or updating your database?')
    if 'y' in answ:
        bot.normal_run()
        while True:
            print('Please enter the songs you want to play.')
            low = input('Starting track number')
            high = input('Ending track number(press enter to play only the starting track)')
            if high == '':
                high = None
            bot.play_song(low_v=low, high_v=high)

    else:
        while True:
            print('Please select the songs you want to play.')
            low = input('Starting track number')
            high = input('Ending track number(press enter to play only the starting track)')
            if high == '':
                high = None
            bot.play_song(low_v=low, high_v=high)
