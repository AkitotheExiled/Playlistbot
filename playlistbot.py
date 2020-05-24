import praw
from threading import Thread
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
from selenium.common.exceptions import NoSuchFrameException, WebDriverException, TimeoutException
import os





class PlaylistBot():

    def __init__(self):
        self.user_agent = "PlaylistBot V0.55 BETA by ScoopJr"
        print('Starting up...', self.user_agent)
        CONFIG = ConfigParser()
        CONFIG.read('config.ini')
        self.user = CONFIG.get('main', 'USER')
        self.password = CONFIG.get('main', 'PASSWORD')
        self.client = CONFIG.get('main', 'CLIENT_ID')
        self.secret = CONFIG.get('main', 'SECRET')
        self.subreddit = CONFIG.get('main', 'SUBREDDIT')
        self.subs = {}
        self.urls = set()
        self.post_link_date = None
        self.now = datetime.now()
        self.thread_running = True
        self.repeat_url = None
        self.to_repeat = False
        self.should_skip = False
        self.should_stop = False
        self.thread_should_stop = False
        self.t1 = None
        # Bot tracking the last post made to scrub video urls
        try:
            with open('lastposttime.txt', 'r') as r:
                data = r.read()
            # self.before is the timestamp used to determine where the bot should start on next run
            self.before = data
            print('The last grabbed posts UTC timestamp is', self.before)
        except IOError:
            print('Could not read file: lastposttime.txt')
            self.before = 'Never.'
        if not self.before:
            self.before = 'Never.'
        # SELENIUM STUFF
        print('Now searching for the appropriate driver.. Please make sure your driver is in the script folder.')
        for filename in os.listdir(os.getcwd()):
            if filename == 'chromedriver.exe':
                try:
                    self.driver = webdriver.Chrome('chromedriver.exe')
                except WebDriverException:
                    print(
                        'MESSAGE: chromedriver.exe needs to be in the same folder as the script. Please contain playlistbot.py and chromedriver.exe in the same folder.')
                    exit()
            if filename == 'geckodriver.exe':
                try:
                    self.driver = webdriver.Firefox('geckodriver.exe')
                except WebDriverException:
                    print(
                        'MESSAGE: geckodriver.exe needs to be in the same folder as the script. Please contain playlistbot.py and geckodriver.exe in the same folder.')
                    exit()
            if filename == 'IEDriverServer.exe':
                try:
                    self.driver = webdriver.Ie('IEDriverServer.exe')
                except WebDriverException:
                    print(
                        'MESSAGE: IEDriverServer.exe needs to be in the same folder as the script. Please contain playlistbot.py and IEDriverServer.exe in the same folder.')
                    exit()
        self.last_post = None



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

    def convert_video_time_to_minute_seconds(self, time_seconds):
        time = divmod(time_seconds, 60)
        return time

    def get_video_time(self, stop):
        is_video_playing = False
        STATES = ( -1, 5)
        while self.thread_running:
            if stop():
                break
            player_state = self.driver.execute_script(
                "return document.getElementById('movie_player').getPlayerState()")
            try:
                print(player_state)
                if player_state in STATES:
                    is_video_playing = False
                video_time = self.driver.execute_script(
                    "return document.getElementById('movie_player').getCurrentTime()")
                video_len = self.driver.execute_script(
                    "return document.getElementById('movie_player').getDuration()")
                if video_time or video_len:
                    cur_time = self.convert_video_time_to_minute_seconds(int(video_time))
                    total_dur = self.convert_video_time_to_minute_seconds(int(video_len))
                    print(f"{cur_time[0]}:{cur_time[1]}/{total_dur[0]}:{total_dur[1]}")
                    print(((cur_time[0] & cur_time[1]) == (total_dur[0] & total_dur[1])))
                    if ((cur_time[0] & cur_time[1]) == (total_dur[0] & total_dur[1])):
                        self.should_skip = True
                        self.thread_should_stop = True
            except NoSuchFrameException:
                continue
            if not is_video_playing:
                if player_state == 1:
                    is_video_playing = True
                if player_state == 0:
                    self.driver.execute_script('document.getElementsByTagName("video")[0].pause()')
                if player_state == -1:
                    try:
                        #self.driver.switch_to.frame(self.driver.find_element_by_id('player'))
                        try:
                            time.sleep(2)
                            self.driver.execute_script("return document.getElementById('movie_player').playVideo()")
                        except Exception as e:
                            print(e)
                        try:
                            WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='ytp-ad-skip-button ytp-button']"))).click()
                        except TimeoutException as e:
                            print(e.msg)
                    except NoSuchFrameException:
                        print('The script could not find the video player.  An ad may be playing right now!')
                if player_state == 5:
                    print("Video has been removed.  Going to next video.")
                    self.should_skip = True
                if player_state == 3:
                    time.sleep(4)
                    self.driver.refresh()
                time.sleep(1)


    def should_skip_song(self, prompt,url=None):
        skip_input = input(prompt)
        if str(skip_input) == 'r' or 'repeat':
            self.to_repeat = True
            self.repeat_url = url
        if str(skip_input) == 'stop':
            self.to_repeat = False
            self.repeat_url = None
            self.should_stop = True
        if 's' or 'y' in str(skip_input):
            self.to_repeat = False
            self.repeat_url = None
            self.should_skip = True
            return


    def play_song(self, low_v, high_v=None):
        self.should_stop = False
        db_func = dataFunc()
        urls = db_func.select_url_between_values(low_val=low_v, high_val=high_v)
        pos, act_urls = zip(*urls)
        for url in act_urls:
            if self.should_stop:
                return
            if self.to_repeat:
                self.driver.get(self.repeat_url)
            else:
                self.driver.get(url)
            while True:
                if self.should_skip or self.should_stop:
                    self.should_skip = False
                    self.thread_running = True
                    break
                self.t1 = Thread(target=self.get_video_time, args=(lambda: self.thread_should_stop))
                self.t1.start()
                t2 = Thread(target=self.should_skip_song,
                            args=('Do you want to skip this song?(type stop to redo track selection)', url))
                t2.start()
                t2.join()

                self.thread_running = False



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
            bot.play_song(low_v=low, high_v=high)
