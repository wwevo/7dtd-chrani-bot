import re
import urllib
from bot.modules.logger import logger
import common


def check_if_player_is_on_whitelist(chrani_bot, player_observer):
    try:
        player_object = chrani_bot.players.get_by_steamid(player_observer.player_steamid)
    except KeyError:
        return

    if player_object.is_online and chrani_bot.whitelist.is_active() is True:
        if not chrani_bot.whitelist.player_is_allowed(player_object):
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "kick", player_object, chrani_bot.settings.get_setting_by_name(name='whitelist_player_unknown_kick_msg', default="You are not on our whitelist. Visit http://chrani.net to find out what that means and if / what options are available to you!"))
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", "{} has been kicked. This is VIP Only!".format(player_object.name), chrani_bot.chat_colors['warning'])
            logger.info("kicked player {} for not being on the whitelist".format(player_object.name))


common.observers_dict["check_if_player_is_on_whitelist"] ={
    "type": "monitor",
    "title": "check_if_player_is_on_whitelist",
    "action": check_if_player_is_on_whitelist,
    "essential": True
}


common.observers_controller["check_if_player_is_on_whitelist"] = {
    "is_active": True
}


def check_if_player_has_url_name(chrani_bot, player_observer):
    try:
        player_object = chrani_bot.players.get_by_steamid(player_observer.player_steamid)
    except KeyError:
        return False

    if player_object.is_online and not chrani_bot.whitelist.player_is_allowed(player_object):
        p = re.search(r"[-A-Z0-9+&@#/%?=~_|!:,.;]{3,}\.[A-Z0-9+&@#/%=~_|]{2,3}$", player_object.name, re.IGNORECASE)
        if p:
            logger.info("kicked player {} for having an URL in the name.".format(player_object.name))
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", "{} has been kicked. we do not allow url-names!".format(player_object.steamid), chrani_bot.chat_colors['warning'])
            chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "kick", player_object, chrani_bot.settings.get_setting_by_name(name='whitelist_url_name_kick_msg', default="We do not allow urls in names. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!"))


common.observers_dict["check_if_player_has_url_name"] = {
    "type": "monitor",
    "title": "check_if_player_has_url_name",
    "action": check_if_player_has_url_name,
    "essential": True
}


common.observers_controller["check_if_player_has_url_name"] = {
    "is_active": True
}


def check_ip_country(chrani_bot, player_observer):
    try:
        try:
            player_object = chrani_bot.players.get_by_steamid(player_observer.player_steamid)
        except KeyError:
            return False

        if player_object.is_blacklisted() or chrani_bot.settings.get_setting_by_name(name='ipinfo.io_password') is None:
            return

        # check if we already know the country code and check against whitelist and banned list
        users_country = player_object.get_country_code()
        if chrani_bot.whitelist.player_is_allowed(player_object) or (users_country is not None and users_country not in chrani_bot.banned_countries_list):
            return False

        try:
            if users_country is None:
                f = urllib.urlopen("https://ipinfo.io/" + player_object.ip + "/country?token=" + str(chrani_bot.settings.get_setting_by_name(name='ipinfo.io_password')))
                users_country = f.read().rstrip()
        except Exception:
            logger.debug("something went wrong in fetching the ipinfo dataset for player {}".format(player_object.name))

        try:
            player_object.set_country_code(users_country)
            chrani_bot.players.upsert(player_object)
        except Exception as e:
            logger.exception(e)

        if player_object.is_online:
            if users_country in chrani_bot.banned_countries_list and chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "kick", player_object, chrani_bot.settings.get_setting_by_name(name='whitelist_blocked_ip_kick_msg', default="Your IP seems to be from a blacklisted country. Visit chrani.net/chrani-bot to find out what that means and if / what options are available to you!")):
                player_object.blacklisted = True
                logger.info("kicked player {} for being from {}".format(player_object.name, users_country))
                chrani_bot.telnet_observer.actions.common.trigger_action(chrani_bot, "say", "{} has been kicked. Blacklisted Country ({})!".format(player_object.name, users_country), chrani_bot.chat_colors['warning'])

    except Exception as e:
        logger.exception(e)
        pass


common.observers_dict["check_ip_country"] = {
    "type": "monitor",
    "title": "check_ip_country",
    "action": check_ip_country,
    "essential": True
}

common.observers_controller["check_ip_country"] = {
    "is_active": True
}
