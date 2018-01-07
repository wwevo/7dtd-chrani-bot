# 7dtd-chrani-bot
A seven days to die Server-Bot to manage players and game-events

this will be added shortly. for now I'll just make a checklist of what I believe works already

bot will start with command-line options for server-configuration
  server-data. debug level can be passed (not exactly thought through)

bot will survive
  * a game-server crash,
  * game-server reboot
  * loss of network connection

bot handles following game-events (I believe are needed for a basic bot)
  * player-death,
  * pleayer-respawn,
  * player-status (alive, dead, in bedroll-screen),
  * player-teleported

i have integrated some portions of the old version, locations are not implemented yet so
it's limited.

basic lobby functions work already

i have hardcoded a lobby suited for Navezgane, so if you want to take this for a spin, it's best to use the
Navezgane map for now

installation:
download files. put on a server or run it at home in a python terminal
to start the bot with full debug output use:

chrani-bot.py 127.0.0.1 8081 12345678 --verbosity=DEBUG

if you want it to be mostly silent use

chrani-bot.py 127.0.0.1 8081 12345678 --verbosity=INFO
 
 xchange ip, port and telnet password with your servers data :)