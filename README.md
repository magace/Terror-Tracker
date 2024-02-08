# Terror Tracker
 Terror tracker that utilizes https://www.d2emu.com/ API thanks to Mysterio. 

**About me and the bot**
I do not do this for a living, I am not very good, but I try to make things I want!  The bot will allow users to request notifications for certain terror zones.  It will notify them one hour before the zone pops up too.
I have not tested this with a very large server, and I am not sure how Discord handles DM throttle rates so if anyone does run into issues please let me know.

**How to setup:**
Download Python and install it if you have not.
I run everything from visual code until I compile it so the next steps could vary.
Open a new terminal (cmd prompt should work too)
Use PIP to install the following packages:
pip install discord  (The newest version of discord.py gave me a ton of trouble.  I had to install Visual Studio as well as Microsoft build tools for the wheel to install)
pip install requests

**Setup your config.json file:**
allowed_channel_ids: Right-click on the discord channel you want to use copy the ID then paste it there.
commant_prefix: This is the command prefix used like .help .notifications .notify .remove .current
bot_name:  This is what the bot will send DMS as
api_url:  Don't edit this unless d2emu changes something.
bot_token:  You must open discord dev tools from a PC and create your own bot user.  This can be a little confusing but you can do it!
show_in_channel: This will update the current TZ in the channel too as well as DM anyone who has subscribed to a zone.

**Start the bot**
Now you can either compile it with pyinstaller, run it from the IDE, or the Python script.
Ctrl + f5 for visual studio code.

**Images and Commands:**

**.help**

![image](https://github.com/magace/Terror-Tracker/assets/7795098/0b60a84d-af7d-42fc-8f27-659396014492)

**.notify zone** (this is just using keywords so it does not need to be exact.  Example: .notify chaos, notify worldstone

![image](https://github.com/magace/Terror-Tracker/assets/7795098/10a43580-e441-4dcc-b61a-689c7c33be9f)

**.remove zone** (same as .notify but removes it from the user's list)

![image](https://github.com/magace/Terror-Tracker/assets/7795098/6fbc6d29-f63d-42f8-8599-9ac740eced61)

**.notifications** (shows a list of the users subscribed zones)

![image](https://github.com/magace/Terror-Tracker/assets/7795098/18137939-aa21-48b9-9051-225da271fedb)

**.current** (just shows current zone.  Useful for me on a small Discord server since I didn't want the channel spamming with every new zone.

![image](https://github.com/magace/Terror-Tracker/assets/7795098/e050d7e4-3ae6-44a3-b44f-d5ae0a29eb4e)

**Direct Message Notifications:**
Note: Users may need to accept DM from the bot.
![image](https://github.com/magace/Terror-Tracker/assets/7795098/313dcdd0-2447-4317-92bb-611de49d58eb)














