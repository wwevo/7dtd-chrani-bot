# 7dtd-chrani-bot
A seven days to die Server-Bot to manage players and game-events

this will be added shortly. for now I'll just make a checklist of what I believe works already

bot will start with command-line options for server-configuration
server-data and debug level can be passed (quick and dirty so it 'works for now')

### what works:

**bot will survive**

  * a game-server crash,
  * game-server reboot
  * loss of network connection

**bot handles following game-events (I believe are needed for a basic bot)**

  * player-death,
  * player-respawn,
  * player-status (alive, dead, in bedroll-screen)
  
you can use Player objects holding data for all online players,
you can also use a Location object in a similar fashion. feel free to invent own actions,
create own usable Objects, share them on github please :) send me a link or simply fork my
project so i get notified :)

with these objects you can write simple and complex actions quickly but still readable. 

**i have implemented a few to demonstrate**

  * basic player greetings
  * lobby
  * home

*i have hardcoded a lobby suited for Navezgane, so if you want to take this for a spin,
it's best to use the Navezgane map for now*

since i haven't decided on a database yet, all data is lost on bot restart, it will survive
a game-server restart / game-server-crash though, so you can test it out for a few days.
nothing for a production server of course ^^

###installation:
download files. put on a server or run it at home in a python terminal

to start the bot with full debug output use:

chrani-bot.py 127.0.0.1 8081 12345678 --verbosity=DEBUG

if you want it to be mostly silent use

chrani-bot.py 127.0.0.1 8081 12345678 --verbosity=INFO
 
 exchange ip, port and telnet password with your servers data :)