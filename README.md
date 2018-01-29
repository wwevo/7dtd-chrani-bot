# 7dtd-chrani-bot
A seven days to die Server-Bot to manage players and game-events

this bot is aimed towards providing simple, hassle-free communities.
we don't try to be the most feature-complete bot, nor do we try to be better than the others or
anything really. we just feel that our needs seem to be different than the needs of most other
servers, and all currently existing managers are simply 'too much' for us

we try to be easy to set up and use. basic lobby and base-building,
controlling the influx of new players, auto-kicking and banning the bad apples. Most of this
should happen automagically. that's about it really. the system is quite easy to extend, so feel
free to develop more elaborate features. this bot will stay simple though.

the bot will start with command-line options for server-configuration.
server-data, debug level and a prfix can be passed, you can run multiple bots from one directory

### what works:

**bot will survive**

  * a game-server crash,
  * game-server reboot
  * loss of network connection
  * a LOT of lag, tested with up to 70 seconds

**the bot monitors all the games telnet messages and handles game-events**

  * player-death, player-respawn,
  * player-status (alive, dead, in bedroll-screen)
  * player-chat (for commands and reactions to anything really)
  
you can use Player objects holding data for all online players
you can also use a Location objects in a similar fashion

with these objects you can write simple and complex actions quickly and human readable. 

**the following functions have been implemented**
(some are finished, some need polishing)

  * player-greetings after login
  * a password protected lobby
  * player-homes with many options
  * some basic location commands. (create, name and set size)
  * a whitelist feature allowing to kick and keep out non-listed players
  * some just for fun commands like fixing a broken leg

since i am not the database guru and am a friend of human readable data, i have decided on
storing all information in .json files. all operations are centralized, so you can easily add
a database if you wish 

###installation:
download files. put them on a server or run them at home in a python terminal

to start the bot with full debug output use:

chrani-bot.py 127.0.0.1 8081 12345678 prefix --verbosity=DEBUG

if you want it to be mostly silent use

chrani-bot.py 127.0.0.1 8081 12345678 prefix --verbosity=INFO
 
 exchange ip, port, telnet password and prefix with your servers data :) the prefix allows for
 several different servers with their own data
 