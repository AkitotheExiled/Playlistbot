# DEMO
![Demo example](example/script_example.gif)

## Driver Guide
For users wanting this script on Chrome, [chromedriver.exe](https://chromedriver.chromium.org/)

For users wanting this script on Firefox, [geckodriver.exe](https://github.com/mozilla/geckodriver/releases)

For users wanting this script on Internet Explorer, [IEDriverServer.exe](https://selenium.dev/downloads/)
### Simple Installation Guide
Step 0. Make sure you have the latest version of this script downloaded.

Step 1. Make sure you have the latest stable verion of your browser downloaded.

Step 2. Download the the latest driver for your browser(see Driver Guide above).

Step 3. Place the driver(the one you just downloaded in Step 2) into the executable folder.

Step 4. Select and click playlistbot.exe in the executable folder and bot should now run!

EXAMPLE OF HOW YOUR EXECUTABLE FOLDER SHOULD LOOK:

>executable

* config.ini

* playlistbot.exe

* chromedriver.exe

#### Original Installation Guide
Step 1. Make sure you have the latest version of this script downloaded.

Step 2. Make sure you have the latest stable verion of your browser downloaded.

Step 3. Organize the bot into a folder, lets call it *PlaylistBot.*

Step 4. Download the the latest driver for your browser(see Driver Guide above).

Step 5. Place your driver into the PlaylistBot folder.

Now your folder should look like this,

>PlaylistBot

* config.ini

* playlistbot.py

* data_func.py

* chromedriver.exe

Step 6. **BEFORE RUNNING THE BOT,** *Install selenium using pip*

>pip install selenium

[how to use pip to install modules/packages?](https://packaging.python.org/tutorials/installing-packages/)

Step 7. Run the script.

Step 8. The script will ask you, 'First run or updating your database?', *reply with yes.*

Step 9. The script will now automatically scrape your subreddit for music posts, and add them into a database. You will be able to tell once you start seeing INSERT INTO Youtube 'httpswww.youtbeurl' print statements.

Step 10. Once it finishes, the bot will ask you if you want to play a song. You will need to enter a number, from 0 to 2056. This song will be your starting point.

>E.G. Enter 0, Song that first plays will be song 0 in database.

Step 11. The bot will ask you for an ending point, You will need to enter a number, from 0 to 2056.

>E.G., typing 10 will make the bot end point be song number 10 in database.

Now the bot will play song 0,1,2,3,4,5,6,7,8,9,10 automatically changing each song as the previous one ends. Once it reaches the final song, song 10 and that song ends. It will ask you again to pick a starting song point, and an ending song point.

##### FAQ

>How do I only play one song?

Enter your starting number, say 0. Then for the ending number, press enter. Now, Song 0 will be the only song that plays.

>Do I always need to type yes when I run the bot?

You will only need to type yes for the first run. You may type yes in follow-up runs to get new music that is added. Otherwise, you may type, no.

>How do I skip a song?

Do type skip and the song will be skipped and press enter.

>What if I want to pause a song?
>
You may pause a song. You WILL have to press play in order for the song to play again. The bot will resume normally afterwards.

>What about my client id and secret key from Reddit, don't I need those?

Fortunately, those are not needed anymore since the bot grabs posts using pushshift's api!

