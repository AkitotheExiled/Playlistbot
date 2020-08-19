import asyncio
from configparser import ConfigParser
from datetime import datetime
from data_func import dataFunc
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchFrameException, WebDriverException, TimeoutException, JavascriptException
import os, sys, time



class PlaylistBot():

    def __init__(self):
        """Create a new PlaylistBot instance.

        """
        self.user_agent = "PlaylistBot V1.0 by ScoopJr"
        print("Starting up...", self.user_agent)
        CONFIG = ConfigParser()
        CONFIG.read("config.ini")
        self.subreddit = CONFIG.get("main", "SUBREDDIT")
        self.urls = set()
        self.now = datetime.now()
        self.should_skip = False
        self.should_stop = False
        self.last_post = None
        self.get_url = None
        self.wrote_utc = None
        self.final_post = None
        self.last_post_time = None
        self.first_run = False
        self.done = False

        self.grab_last_post_time_file()
        self.check_for_webdriver()

    def grab_last_post_time_file(self):
        """Checks for lastposttime.txt and if it exists use the UTC inside as a reference for the last post grabbed.  Otherwise make new file"""
        try:
            with open("lastposttime.txt", "r") as r:
                data = r.read()
            # self.before is the timestamp used to determine where the bot should start on next run
            if data == "None":
                self.before = "Never."
            else:
                self.before = data
                print("The last grabbed posts UTC timestamp is", self.before)
                self.wrote_utc = True
        except IOError:
            print("Could not read file: lastposttime.txt")
            self.before = "Never."
            self.first_run = True
            self.wrote_utc = False
        if not self.before or self.before is None:
            self.before = "Never."

    def check_for_webdriver(self):
        """Checks for the following webdrivers:
        chromedriver.exe
        geckodriver.exe
        IEDriverserver.exe

        in the webdriver folder.
        """
        print("Now searching for the appropriate driver.. Please make sure your driver is in the script folder.")
        for filename in os.listdir(os.getcwd()):
            if filename == "chromedriver.exe":
                try:
                    self.driver = webdriver.Chrome("chromedriver.exe")
                except WebDriverException:
                    print(
                        "MESSAGE: chromedriver.exe was not found.  Please download chromedriver.exe from "
                        " https://chromedriver.chromium.org/" + "." )
                    print("MESSAGE: Make sure chromedriver.exe and playlistbot.exe are in the same folder!")
                    exit()
            elif filename == "geckodriver.exe":
                try:
                    self.driver = webdriver.Firefox("geckodriver.exe")
                except WebDriverException:
                    print(
                        "MESSAGE: geckodriver.ex was not found.  Please download geckodriver.ex from "
                        " https://github.com/mozilla/geckodriver/releases" + ".")
                    print("MESSAGE: Make sure geckodriver.ex and playlistbot.exe are in the same folder!")
                    exit()
            elif filename == "IEDriverServer.exe":
                try:
                    self.driver = webdriver.Ie("IEDriverServer.exe")
                except WebDriverException:
                    print(
                        "MESSAGE: IRDriverServer.exe was not found.  Please download IRDriverServer.exe from "
                        " https://selenium-release.storage.googleapis.com/index.html" + ".")
                    print("MESSAGE: Make sure IRDriverServer.exe and playlistbot.exe are in the same folder!")
                    exit()
            elif filename == "webdriver":
                try:
                    os.chdir("webdriver")
                    for file in os.listdir(os.getcwd()):
                        if file == "chromedriver.exe":
                            try:
                                self.driver = webdriver.Chrome("chromedriver.exe")
                            except WebDriverException:
                                print(
                                    "MESSAGE: chromedriver.exe was not found.  Please download chromedriver.exe from "
                                    " https://chromedriver.chromium.org/" + ".")
                                print("MESSAGE: Make sure chromedriver.exe and playlistbot.exe are in the same folder!")
                                exit()
                        elif file == "geckodriver.exe":
                            try:
                                self.driver = webdriver.Firefox("geckodriver.exe")
                            except WebDriverException:
                                print(
                                    "MESSAGE: geckodriver.ex was not found.  Please download geckodriver.ex from "
                                    " https://github.com/mozilla/geckodriver/releases" + ".")
                                print("MESSAGE: Make sure geckodriver.ex and playlistbot.exe are in the same folder!")
                                exit()
                        elif file == "IEDriverServer.exe":
                            try:
                                self.driver = webdriver.Ie("IEDriverServer.exe")
                            except WebDriverException:
                                print(
                                    "MESSAGE: IRDriverServer.exe was not found.  Please download IRDriverServer.exe from "
                                    " https://selenium-release.storage.googleapis.com/index.html" + ".")
                                print("MESSAGE: Make sure IRDriverServer.exe and playlistbot.exe are in the same folder!")
                                exit()
                except:
                    print("Unable to change directory.  Make sure webdriver folder exists.")


    def grab_urls(self):
        """
        Retrieves all Youtube URL links from /r/musicforpeople since it was created(Jan 19, 2019)
        Sorts them into a set
        Returns the sorted URLS in a set once no more Youtube LINKS can be pulled from the API
        """
        i = 0
        headers = {'user-agent': 'Playlistbot 1.0 by ScoopJr'}
        while i <= 0:
            time.sleep(3)
            subreddit = self.subreddit
            size = 100
            print(self.before == "Never.")
            if (self.first_run or (self.before == "Never.") ):
                befor = "1h"
                after = 1547856000
            elif self.first_run or not self.done:
                befor = self.before
                after = 1547856000
            else:
                befor = "1h"
                after = self.before
            start = time.time()

            url = "https://api.pushshift.io/reddit/submission/search/?subreddit={}&sort=desc&sort_type=created_utc&size={}&after={}&before={}".format(
                subreddit, size, after, befor)
            response = requests.get(url, headers=headers).json()
            stop = time.time()
            print("Elapsed in seconds:" + str(stop - start))
            if response["data"]:
                print("Songs are being found...")
                for item in response["data"]:
                    print(f"Adding {item['url']}")
                    self.urls.add(item["url"])
                    if not self.wrote_utc:
                        self.last_post_time = item["created_utc"]
                        self.wrote_utc = True

                    self.final_post = item["created_utc"]
                self.before = self.final_post
                i+=1
            else:
                if self.last_post_time is None:
                    print("No new songs found.  Returning to track selection.")
                    return list(self.urls)
                else:
                    self.done = True
                    with open("lastposttime.txt", "w+") as f:
                        f.write(str(self.last_post_time))
                        f.close()
                    return list(self.urls)
        with open("lastposttime.txt", "w+") as f:
            f.write(str(self.last_post_time))
            f.close()
        return list(self.urls)


    def sort_urls_by_domain(self, urls):
        """
        urls - a mutable list that should contain links to youtube, and soundcloud
        It categorizes the links into Youtube, and Soundcloud and returns a dict with the keys, youtube, and soundcloud, and other.
        """
        try:
            urls2 = list(urls)
        except TypeError as e:
            return print(e)
        sc_list = []
        other_list = []
        youtube_list = []
        for url in urls2:
            if (("youtube" in url) or ("youtu.be" in url)) & ("reddit" not in url):
                youtube_list.append(url)
            if "soundcloud" in url:
                sc_list.append(url)
            if "youtube" not in url and "soundcloud" not in url and "youtu.be" not in url:
                other_list.append(url)
        return {"youtube": youtube_list, "soundcloud": sc_list, "other": other_list}


    def convert_video_time_to_minute_seconds(self, time_seconds):
        """
        time_seconds - integer value that represents time in seconds(I.E. 300 time_seconds = 300 seconds)
        Returns a tuple of the form (minute, seconds)

        I.E.
        convert_video_time_to_minute_seconds(300)
        returns (5,0)
        """
        time = divmod(time_seconds, 60)
        if time[1] < 10:
            new_time = list(time)
            new_time[1] = f"0{str(time[1])}"
            time = tuple(new_time)
        return time

    def return_video_duration_in_seconds(self):
        """
        Executes Javascript - player.getDuration() to return video duration in seconds
        """
        video_len = self.driver.execute_script(
            "return document.getElementById('movie_player').getDuration()")
        return video_len

    def return_video_title(self):
        """
        Executes Javascropt - player.getVideoData().title
        player.getVideoData() - Youtube API to return player data
        .title - attribute referring to video title
        returns video title
        """
        video_title = self.driver.execute_script(
            "return document.getElementById('movie_player').getVideoData().title")
        return video_title

    def ad_removal_before_video(self):
        """
        Waits 15 seconds until the button, skip ad, on youtube is clickable and clicks it.
        Otherwise, it times out and trys to play the video using player.playVideo()
        """
        try:
            # self.driver.switch_to.frame(self.driver.find_element_by_id('player'))
            try:
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[@class='ytp-ad-skip-button ytp-button']"))).click()
            except TimeoutException as e:
                try:
                    self.driver.execute_script("return document.getElementById('movie_player').playVideo()")
                except:
                    pass
        except NoSuchFrameException:
            print("The script could not find the video player.  An ad may be playing right now!")

    async def aio_readline(self, loop):
        """
        async input function
        loop - the current running loop
        If the user input contains, 'y' then it changes the condition of skip to True and awaits to allow asyncio to skip the song
        If the user input contains, 's' then it changes the condition of stop to True and awaits to allow asyncio to stop the current song selection
        """
        while True:
            if self.should_stop:
                return
            print("Type yeah to skip song.  Type stop to stop selection.")

            line = await loop.run_in_executor(None, sys.stdin.readline)
            if "y" in line:
                self.should_skip = True
                await asyncio.sleep(1)
                print("skip should hapopen")
            if "s" in line:
                self.should_stop = True
                return
            print("y" in line)


    def player_state_logic(self):
        """ Contains the logic for the different states of the player on Youtube.
        1 = video is playing - function returns since that is default playback
        0 = video is paused - function does nothing
        -1 = video is not playing(usually an ad is playing) - runs ad_removal_before_video()
        3 = buffering - lets video buffer
        5 = Video is queued - video may not be available and sets skip condition to True

        """
        try:
            player_state = self.driver.execute_script(
                "return document.getElementById('movie_player').getPlayerState()")
            print(f"PLAYERSTATE: {player_state}")
            if player_state is (1 or 3):
                return
            elif player_state == -1:
                self.ad_removal_before_video()
            elif player_state == 0:
                self.driver.execute_script("return document.getElementById('movie_player').playVideo()")
                    #self.driver.execute_script('document.getElementsByTagName("video")[0].pause()')
            elif player_state == 5:
                print("Video has been removed.  Going to next video.")
                self.should_skip = True
        except JavascriptException:
            return

    async def get_video_time(self):
        """Gets the video playtime and presents it to the user in a readable format."""
        self.player_state_logic()
        while True:
            if self.should_stop:
                return
            try:
                video_time = self.driver.execute_script(
                    "return document.getElementById('movie_player').getCurrentTime()")
                video_len = self.driver.execute_script(
                    "return document.getElementById('movie_player').getDuration()")
                if video_len == 0: # Video may have been removed - call player_state_logic() to skip song
                    self.player_state_logic()
                    await asyncio.sleep(1)
                elif video_time or video_len:
                    if video_time == 0: # Video may be stuck on an ad
                        self.player_state_logic()
                    cur_time = self.convert_video_time_to_minute_seconds(int(video_time))
                    total_dur = self.convert_video_time_to_minute_seconds(int(video_len))
                    title = self.return_video_title()
                    print(f"{title}\n{cur_time[0]}:{cur_time[1]}/{total_dur[0]}:{total_dur[1]}")
                    await asyncio.sleep(1)
                    if ((cur_time[0] == total_dur[0]) and (cur_time[1] == total_dur[1])):
                        self.should_skip = True
            except NoSuchFrameException:
                continue









    async def play_song(self, start, stop=None):
        """Handles the playing of a song, takes a starting value, and an ending value"""
        self.should_stop = False
        db_func = dataFunc()
        urls = db_func.select_url_between_values(low_val=start, high_val=stop)
        pos, act_urls = zip(*urls)
        for url in act_urls:
            if self.should_stop:
                return
            self.should_skip = False
            self.get_url = True
            self.driver.get(url)
            while True:
                self.get_url = False
                if self.should_skip or self.should_stop:
                    break
                else:
                    await asyncio.sleep(1)
        self.should_stop = True
        return



    async def scheduled_tasks(self, start, stop, stop_flag=False):
        """Scheduling tasks for running"""
        loop = asyncio.get_event_loop()
        # tasks_for_each_url
        task_per_url = []
        # main task
        mtask = self.play_song(start, stop)
        # as long main task is running, each url in the for loop, run tasks_for_each_url
        main_task = loop.create_task(mtask)
        task2 = loop.create_task(self.get_video_time())
        task1 = loop.create_task(self.aio_readline(loop))
        await asyncio.gather(main_task,task2,task1) # running all tasks at once
        main_task_is_done = main_task.done()
        while not main_task_is_done: # If other tasks stop and we're still playing songs, run them again
            print("in while")
            await asyncio.sleep(1)
            if task_per_url:
                print((task2) in task_per_url)
                continue
            elif not task_per_url:
                print(task_per_url)
                if (task2.done() and task1.done()):
                    task_per_url.append(task2)
                    task_per_url.append(task1)
                    for task in task_per_url:
                        print("await task")
                        await task
                else:
                    await asyncio.sleep(1)
        return








    def update_database(self):
        """
        Handles the updating of the database.

        """
        print("Updating the database, this may take a while.")
        self.grab_last_post_time_file()
        while not self.done:
            self.grab_urls()
            data = self.sort_urls_by_domain(list(self.urls))
            data_func = dataFunc()
            for url in data["youtube"]:
                data_func.insert_into_table(pos=data["youtube"].index(url), url=url)
        return True

def get_int(prompt, allow_empty=False):
    """
     prompt: - The text displayed to the user so they respond
     allow_empty: - Allows the user to enter an empty string
     default: returns integer representation of user input
     if allow_empty = True,
     allows user to return empty string
    """
    while True:
        user_input = input(prompt)
        if allow_empty & (user_input == ""):
            return user_input
        else:
            try:
                int(user_input)
            except ValueError:
                print("Make your input an integer")
            else:
                return int(user_input)






if __name__ == "__main__":
    bot = PlaylistBot()
    def run():
        while True:
            df = dataFunc()
            link_count = df.count_links_and_print()
            print(f"Please select the songs you want to play.(TOTAL SONGS AVAILABLE: {link_count[0]})")
            low = get_int("Starting track number\n")

            high = get_int("Ending track number(press enter to play only the starting track)\n", allow_empty=True)

            if high == "":
                print(f"Playing single track: {low}")
                loop = asyncio.get_event_loop()
                loop.run_until_complete(bot.scheduled_tasks(start=low, stop=high))
            elif low > high:
                print(f"Your start track value: {low}, cannot be greater than your stop track value: {high}")
                continue
            else:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(bot.scheduled_tasks(start=low, stop=high))

    if bot.first_run:
        print("Now getting the required songs from the subreddit.")
        bot.update_database()
        run()
    else:
        answ = input("Do you want to check for new songs?")
        if "y" in answ:
            bot.update_database()
            run()
        else:
            run()


