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