import os
import sys
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from glob import glob
import json
import subprocess
import urllib2
import traceback
import datetime
import time
import operator
import string
import uuid

from _winreg import *
from xml.etree import ElementTree as ET
from xml.dom import minidom
from resources.lib.steamgame import SteamGame
from resources.lib.origingame import OriginGame
from resources.lib.goggame import GogGame
from resources.lib.uplaygame import UplayGame
from resources.lib.battlegame import BattleGame

import resources.lib.common as common
from resources.lib.common import log
from resources.lib.common import localize
from xml.dom.minidom import parse
from xml.dom.minidom import Document

__addon__ = common.__addon__
__addonid__ = common.__addonid__
__addonversion__ = common.__addonversion__
__addonname__ = common.__addonname__
__addonpath__ = common.__addonpath__
__icon__ = common.__icon__

# Addon paths definition
PLUGIN_DATA_PATH = xbmc.translatePath(os.path.join("special://profile/addon_data", __addonid__))
BASE_PATH = xbmc.translatePath(os.path.join("special://", "profile"))
HOME_PATH = xbmc.translatePath(os.path.join("special://", "home"))
FAVOURITES_PATH = xbmc.translatePath('special://profile/favourites.xml')
ADDONS_PATH = xbmc.translatePath(os.path.join(HOME_PATH, "addons"))
CURRENT_ADDON_PATH = xbmc.translatePath(os.path.join(ADDONS_PATH, __addonid__))
ADDONS_MEDIA_PATH = xbmc.translatePath(os.path.join(CURRENT_ADDON_PATH, 'resources', 'skins', 'Default', 'media'))
CURRENT_ADDON_LIB_PATH = xbmc.translatePath(os.path.join(ADDONS_PATH, __addonid__, "resources", "lib"))
GAMES_DB_PATH = os.path.join(PLUGIN_DATA_PATH, "games.db")
DEFAULT_THUMB_PATH = os.path.join(PLUGIN_DATA_PATH, "thumbs")
DEFAULT_FANART_PATH = os.path.join(PLUGIN_DATA_PATH, "fanarts")
CUSTOM_GAME_TYPE = '1008'


class Game(object):
    def __init__(self, gameId, title, type, path, thumbImage, fanartImage, isNameChanged, isPathChanged, isIconChanged,
                 isFanartChanged):
        self.gameId = gameId
        self.title = title
        self.type = type
        self.path = path
        self.thumbImage = thumbImage
        self.fanartImage = fanartImage
        self.isNameChanged = isNameChanged
        self.isPathChanged = isPathChanged
        self.isIconChanged = isIconChanged
        self.isFanartChanged = isFanartChanged

def getSteamExePath():
        import errno, sys, _winreg
        steamExe = ''

        try:
            if sys.maxsize > 2**32:
                arch_keys = {_winreg.KEY_WOW64_32KEY, _winreg.KEY_WOW64_64KEY}
            else:
                arch_keys = {_winreg.KEY_READ}

            for arch_key in arch_keys:

                key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", 0, _winreg.KEY_READ | arch_key)
                try:
                    steamExe = _winreg.QueryValueEx(key, 'InstallPath')[0] + "\\steam.exe"
                except OSError as e:
                    if e.errno == errno.ENOENT:
                        # DisplayName doesn't exist in this skey
                        pass
                finally:
                    key.Close()
        except Exception,e:
            log(e.message)
            log(e.__class__.__name__)
            traceback.print_exc(e)
    
        return steamExe

def getUuid():
    return uuid.uuid4().get_hex()

def getSafeFileName(fileName):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in fileName if c in valid_chars)


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


def writeToGameDB(games):
    gamesDbObj = open(GAMES_DB_PATH, 'w')
    gamesDbObj.write(json.dumps(games))
    gamesDbObj.close()

def getProgramUrl(game, path):

    url = build_url(
            {'mode': 'folder', 'action': 'launchgame', 'gameid': game.gameId, 'gametype': game.type,
                                 'gamepath': game.path})

    return url

def getMenuInfo(menuType):
    title = ''
    buttonPrefix = ''
    if menuType == 'home':
            buttonPrefix = 'HomeMenuButton'
            title = localize(33024)
    elif menuType == 'sub':
        buttonPrefix = 'HomeGameButton'
        title = localize(33025)
        
    return title, buttonPrefix


def removeFromHomeMenu(selectedProgram, menuType):
    if selectedProgram:

        title, buttonPrefix = getMenuInfo(menuType)


        for i in range(1, 6, 1):
            buttonValue = xbmc.getInfoLabel('Skin.String({0}{1})'.format(buttonPrefix, i))
            if buttonValue:
                addonId = xbmc.getInfoLabel('System.AddonTitle({0})'.format(buttonValue))

                if not addonId:
                    if xbmc.getInfoLabel('Skin.String({0}{1}Type)'.format(buttonPrefix, i)) == 'launcher':
                        if xbmc.getInfoLabel('Skin.String({0}{1}TypeId)'.format(buttonPrefix, i)) == selectedProgram.gameId:
                            xbmc.executebuiltin('Skin.SetString({0}{1}, '')'.format(buttonPrefix, i))
                            xbmc.executebuiltin('Skin.SetString({0}{1}Title, '')'.format(buttonPrefix, i))
                            xbmc.executebuiltin('Skin.SetString({0}{1}Image, '')'.format(buttonPrefix, i))
                            xbmc.executebuiltin('Skin.SetString({0}{1}Type, '')'.format(buttonPrefix, i))
                            xbmc.executebuiltin('Skin.SetString({0}{1}TypeId, '')'.format(buttonPrefix, i))

                            programJson = getGameJson()
                            if menuType == 'home':
                                programJson[selectedProgram.gameId]['addedToMainMenu'] = False
                            elif menuType == 'sub':
                                programJson[selectedProgram.gameId]['addedToSubMenu'] = False

                            #writeToDB(programJson)

                            break


def addtoHomeMenu(selectedProgram, menuType, path):
    if selectedProgram:
        myurl = getProgramUrl(selectedProgram, path)
        optionToShow = []

        title, buttonPrefix = getMenuInfo(menuType)

        for i in range(1, 6, 1):
            buttonValue = xbmc.getInfoLabel('Skin.String({0}{1})'.format(buttonPrefix, i))
            if buttonValue:
                addonId = xbmc.getInfoLabel('System.AddonTitle({0})'.format(buttonValue))

                if addonId:
                    optionToShow.append(xbmc.getLocalizedString(24000) + ' {0}        {1}'.format(i, addonId))
                else:
                    optionToShow.append(xbmc.getLocalizedString(24000) + ' {0}        {1}'.format(i, xbmc.getInfoLabel('Skin.String({0}{1}Title)'.format(buttonPrefix, i))))
            else:
                optionToShow.append(xbmc.getLocalizedString(24000) + ' {0}'.format(i))

        dialog = xbmcgui.Dialog()
        retVal = dialog.select(title,optionToShow)
        if retVal != -1:
            position = retVal + 1

            xbmc.executebuiltin('Skin.SetString({0}{1}, {2})'.format(buttonPrefix ,position, myurl))
            xbmc.executebuiltin('Skin.SetString({0}{1}Title, {2})'.format(buttonPrefix ,position, selectedProgram.title))
            xbmc.executebuiltin('Skin.SetString({0}{1}Image, {2})'.format(buttonPrefix ,position, selectedProgram.thumbImage))
            xbmc.executebuiltin('Skin.SetString({0}{1}Type, {2})'.format(buttonPrefix ,position, 'launcher'))
            xbmc.executebuiltin('Skin.SetString({0}{1}TypeId, {2})'.format(buttonPrefix ,position, selectedProgram.gameId))

            programJson = getGameJson()

            if menuType == 'home':
                programJson[selectedProgram.gameId]['addedToMainMenu'] = True
            elif menuType == 'sub':
                programJson[selectedProgram.gameId]['addedToSubMenu'] = True

            #writeToDB(programJson)

def findGames():
    games = {}

    orgGames = getGames()
    isCanceled = False

    #find all custom installed games
    for game in orgGames:
        if (game.type == CUSTOM_GAME_TYPE):
            gameId = game.gameId
            games[gameId] = {}
            games[gameId]['name'] = game.title
            games[gameId]['path'] = game.path
            games[gameId]['isNameChanged'] = game.isNameChanged
            games[gameId]['isPathChanged'] = game.isPathChanged
            games[gameId]['isIconChanged'] = game.isIconChanged
            games[gameId]['isFanartChanged'] = game.isFanartChanged
            games[gameId]['type'] = game.type
            games[gameId]['thumbImage'] = game.thumbImage
            games[gameId]['fanartImage'] = game.fanartImage

    steamGame = SteamGame(DEFAULT_THUMB_PATH, DEFAULT_FANART_PATH)
    if (not isCanceled):
        games, isCanceled = steamGame.findGames(orgGames, games)

    originGame = OriginGame(DEFAULT_THUMB_PATH, DEFAULT_FANART_PATH)
    if (not isCanceled):
        games, isCanceled = originGame.findGames(orgGames, games)

    gogGame = GogGame(DEFAULT_THUMB_PATH, DEFAULT_FANART_PATH)
    if (not isCanceled):
        games, isCanceled = gogGame.findGames(orgGames, games)

    uplayGame = UplayGame(DEFAULT_THUMB_PATH, DEFAULT_FANART_PATH)
    if (not isCanceled):
        games, isCanceled = uplayGame.findGames(orgGames, games)

    battleGame = BattleGame(DEFAULT_THUMB_PATH, DEFAULT_FANART_PATH)
    if (not isCanceled):
        games, isCanceled = battleGame.findGames(orgGames, games)
    
    if(not isCanceled):
        for game in orgGames:
            if (game.type == 0 or game.type == int(CUSTOM_GAME_TYPE)):
                gameId = game.gameId
                games[gameId] = {}
                games[gameId]['name'] = game.title
                games[gameId]['path'] = game.path
                games[gameId]['isNameChanged'] = game.isNameChanged
                games[gameId]['isPathChanged'] = game.isPathChanged
                games[gameId]['isIconChanged'] = game.isIconChanged
                games[gameId]['isFanartChanged'] = game.isFanartChanged
                games[gameId]['type'] = game.type
                games[gameId]['thumbImage'] = game.thumbImage
                games[gameId]['fanartImage'] = game.fanartImage

        for game in games:
            if (game.title == ''):
                games.pop(game)

        writeToGameDB(games)
        dialog = xbmcgui.Dialog()
        ok = dialog.ok(__addonname__, str(len(games) - 1) + ' ' + localize(33004))

    # if (counter > 0):
    # xbmc.executebuiltin('Container.Update("plugin://plugin.program.aw.gamelauncher/?action=games&amp;mode=folder")')


def getGames():
    games = []

    if (os.path.isfile(GAMES_DB_PATH)):
        gamesDbfile = open(GAMES_DB_PATH, 'r')
        gamesJson = json.loads(gamesDbfile.read())
        gamesDbfile.close()

        for game in gamesJson:
            games.append(Game(game, gamesJson[game]['name'], gamesJson[game]['type'], gamesJson[game]['path'],
                              gamesJson[game]['thumbImage'], gamesJson[game]['fanartImage'],
                              gamesJson[game]['isNameChanged'], gamesJson[game]['isPathChanged'],
                              gamesJson[game]['isIconChanged'], gamesJson[game]['isFanartChanged']))

    return games


def getGameJson():
    gamesJson = ''

    if (os.path.isfile(GAMES_DB_PATH)):
        gamesDbfile = open(GAMES_DB_PATH, 'r')
        gamesJson = json.loads(gamesDbfile.read())
        gamesDbfile.close()

    return gamesJson


def getGameDictionary():
    existinGames = getGames()
    games = {}

    for game in existinGames:
        gameId = game.gameId
        games[gameId] = {}
        games[gameId]['name'] = game.title
        games[gameId]['path'] = game.path
        games[gameId]['isNameChanged'] = game.isNameChanged
        games[gameId]['isPathChanged'] = game.isPathChanged
        games[gameId]['isIconChanged'] = game.isIconChanged
        games[gameId]['isFanartChanged'] = game.isFanartChanged
        games[gameId]['type'] = game.type
        games[gameId]['thumbImage'] = game.thumbImage
        games[gameId]['fanartImage'] = game.fanartImage

    return games


def isInFavorites(game):
    if os.path.isfile(FAVOURITES_PATH):
        fav_xml = parse(FAVOURITES_PATH)
        fav_doc = fav_xml.documentElement.getElementsByTagName('favourite')
        for count, favourite in enumerate(fav_doc):
            if (favourite.attributes[
                    'name'].nodeValue == game.title and favourite.firstChild.data == getGameLaunchUrlAction(game)):
                return True
    else:
        return False


def getGameLaunchUrlAction(game):
    return 'PlayMedia("{0}")'.format(
        build_url({'mode': 'folder', 'action': 'launchgame', 'gameid': game.gameId, 'gametype': game.type}))

def isAddedtoMenu(buttonPrefix,programId):
    isSubMenuExist = False
    for i in range(1, 6, 1):
        addonId = ''
        buttonValue = xbmc.getInfoLabel('Skin.String({0}{1})'.format(buttonPrefix, i))
        if not buttonValue:
            addonId = xbmc.getInfoLabel('System.AddonTitle({0})'.format(buttonValue))

        if not addonId:
            if xbmc.getInfoLabel('Skin.String({0}{1}Type)'.format(buttonPrefix, i)) == 'launcher':
                if xbmc.getInfoLabel('Skin.String({0}{1}TypeId)'.format(buttonPrefix, i)) == programId:
                    isSubMenuExist = True
                    break
    return isSubMenuExist

def addContextMenu(game, listItem):
    menuTuple = None

    homeMenuAction = 'addtohomemenu'
    homeMenuTitle = localize(33018)
    isGameAdded = isAddedtoMenu('HomeMenuButton', game.gameId)
    if isGameAdded:
        homeMenuAction = 'removefromhomemenu'
        homeMenuTitle = localize(33019)

    subMenuAction = 'addtogamesubmenu'
    subMenuTitle = localize(33020)
    isSubMenuAdded = isAddedtoMenu('HomeGameButton', game.gameId)
    if isSubMenuAdded:
        subMenuAction = 'removefromgamesubmenu'
        subMenuTitle = localize(33021)

    if (isInFavorites(game)):
        menuTuple = (xbmc.getLocalizedString(14077),
                     'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=removefromfavorites&amp;mode=context&amp;gameid={0})'.format(
                         game.gameId),)
    else:
        menuTuple = (xbmc.getLocalizedString(14076),
                     'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=addtofavorites&amp;mode=context&amp;gameid={0})'.format(
                         game.gameId),)
    if (game.type == 0):
        listItem.addContextMenuItems([], True)
    elif (game.type != CUSTOM_GAME_TYPE):
        listItem.addContextMenuItems([menuTuple,
                                      (localize(33005),
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=edittitle&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),),
                                      (localize(33007),
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=editicon&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),),
                                      (localize(33008),
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=editfanart&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),),
                                      (homeMenuTitle,
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction='+ homeMenuAction +'&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),),
                                      (subMenuTitle,
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction='+ subMenuAction +'&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),), ], True)
    else:
        listItem.addContextMenuItems([menuTuple,
                                      (localize(33005),
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=edittitle&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),),
                                      (localize(33006),
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=editicon&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),),
                                      (localize(33008),
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=editfanart&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),),
                                      (homeMenuTitle,
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction='+ homeMenuAction +'&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),),
                                      (subMenuTitle,
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction='+ subMenuAction +'&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),),
                                      (localize(33026),
                                       'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=remove&amp;mode=context&amp;gameid={0})'.format(
                                           game.gameId),), ], True)


def addToFavorite(game):
    doc = None
    root = None

    if (not os.path.isfile(FAVOURITES_PATH)):
        doc = Document()
        root = doc.createElement("favourites")
        doc.appendChild(root)
    else:
        doc = parse(FAVOURITES_PATH)
        root = doc.documentElement

    favNode = doc.createElement("favourite")
    root.appendChild(favNode)

    favNode.setAttribute("name", game.title)
    favNode.setAttribute("thumb", game.thumbImage)

    url = getGameLaunchUrlAction(game)

    textNode = doc.createTextNode(url)
    favNode.appendChild(textNode)

    doc.writexml(open(FAVOURITES_PATH, 'w'))

    doc.unlink()


def removeFromFavorite(game):
    if os.path.isfile(FAVOURITES_PATH):
        doc = parse(FAVOURITES_PATH)
        fav_doc = doc.documentElement.getElementsByTagName('favourite')
        for count, favourite in enumerate(fav_doc):
            if (favourite.attributes[
                    'name'].nodeValue == game.title and favourite.firstChild.data == getGameLaunchUrlAction(game)):
                doc.documentElement.removeChild(favourite)
                break;

    doc.writexml(open(FAVOURITES_PATH, 'w'))

    doc.unlink()

def writeToDB(programs):
    programsDBfile = open(GAMES_DB_PATH, 'w')
    programsDBfile.write(json.dumps(programs))
    programsDBfile.close()

def updateGameInformation(orgGame, property, value):
    if (os.path.isfile(GAMES_DB_PATH)):
        gamesDbfile = open(GAMES_DB_PATH, 'r')
        gamesJson = json.loads(gamesDbfile.read())
        gamesDbfile.close()

        for game in gamesJson:
            if (game == orgGame.gameId):

                if (property == 'title'):
                    gamesJson[game]['name'] = value
                    gamesJson[game]['isNameChanged'] = 1
                    orgGame.title = value
                    orgGame.isNameChanged = 1
                elif (property == 'icon'):
                    gamesJson[game]['thumbImage'] = value
                    gamesJson[game]['isIconChanged'] = 1
                    orgGame.thumbImage = value
                    orgGame.isIconChanged = 1
                elif (property == 'fanart'):
                    gamesJson[game]['fanartImage'] = value
                    gamesJson[game]['isFanartChanged'] = 1
                    orgGame.fanartImage = value
                    orgGame.isFanartChanged = 1
                elif (property == 'title'):
                    gamesJson[game]['title'] = value
                break;

        gamesDbfile = open(GAMES_DB_PATH, 'w')
        gamesDbfile.write(json.dumps(gamesJson))
        gamesDbfile.close()


def get_view_mode():
    view_mode = 50
    for id in range(50, 59 + 1):
        try:
            if xbmc.getCondVisibility("Control.IsVisible(%i)" % id):
                view_mode = repr(id)
                return view_mode
                break
        except:
            pass

    for id in range(500, 600 + 1):
        try:
            if xbmc.getCondVisibility("Control.IsVisible(%i)" % id):
                view_mode = repr(id)
                return view_mode
                break
        except:
            pass

    return view_mode

def extractIcon(filePath, extractIconPath):
    return AlphaUIUtils.GetIconFromExecutable(unicode(filePath), unicode(extractIconPath))

def findSelectedGame(games, gameId):
    for game in games:
        if game.gameId == gameId:
            return game


def removeGame(game):
   
    games = getGameJson()

    for i in games:
        if games[i]['name'] == game.title and games[i]['path'] == game.path:
            games.pop(i)
            break

    writeToDB(games)

if (xbmcgui.Window(10004).getProperty('service.aw.customizations.isComponentInstalled') == "False"):
    customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
    customizationAddonLanguage = customizationAddon.getLocalizedString

    xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33011))
else:
    import AlphaUIUtils

    base_url = sys.argv[0]
    addon_handle = int(sys.argv[1])
    args = urlparse.parse_qs(sys.argv[2][1:])

    mode = args.get('mode', None)

    # xbmcplugin.setContent(int(sys.argv[1]), 'games')

    # log("base_url => + " + base_url + ", args => " + sys.argv[2][1:])

    if mode is None:

        imageFilePath = os.path.join(CURRENT_ADDON_PATH, 'resources', 'skins', 'Default', 'media', 'alienware')
        noOfItems = 7

        url = build_url({'mode': 'folder', 'action': 'games'})
        li = xbmcgui.ListItem(localize(33000), iconImage=os.path.join(imageFilePath, 'games.png'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, totalItems=noOfItems, isFolder=True)

        url = build_url({'mode': 'folder', 'action': 'findgames'})
        li = xbmcgui.ListItem(localize(33001), iconImage=os.path.join(imageFilePath, 'findgames.png'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, totalItems=noOfItems, isFolder=True)

        url = build_url({'mode': 'folder', 'action': 'launchsteam'})
        li = xbmcgui.ListItem(localize(33002), iconImage=os.path.join(imageFilePath, 'steam.png'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, totalItems=noOfItems, isFolder=True)

        url = build_url({'mode': 'folder', 'action': 'launchorigin'})
        li = xbmcgui.ListItem(localize(33009), iconImage=os.path.join(imageFilePath, 'origin.png'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, totalItems=noOfItems, isFolder=True)

        #url = build_url({'mode': 'folder', 'action': 'launchgog'})
        #li = xbmcgui.ListItem(localize(33010), iconImage=os.path.join(imageFilePath, 'gog.png'))
        #xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
        #                            listitem=li, totalItems=noOfItems, isFolder=True)

        url = build_url({'mode': 'folder', 'action': 'launchuplay'})
        li = xbmcgui.ListItem(localize(33011), iconImage=os.path.join(imageFilePath, 'uplay.png'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, totalItems=noOfItems, isFolder=True)

        url = build_url({'mode': 'folder', 'action': 'launchbattle'})
        li = xbmcgui.ListItem(localize(33012), iconImage=os.path.join(imageFilePath, 'battle.png'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, totalItems=noOfItems, isFolder=True)

        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

    elif (mode[0] == 'folder'):
        

        actionName = args['action'][0]

        if (actionName == 'launchsteam'):
            xbmc.executebuiltin('RunAddon(script.aw.steam.launcher)')
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Refresh("plugin://plugin.program.aw.gamelauncher")')
        elif (actionName == 'launchorigin'):
            xbmc.executebuiltin('RunAddon(script.aw.origin.launcher)')
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Refresh("plugin://plugin.program.aw.gamelauncher")')
        elif (actionName == 'launchgog'):            
            xbmc.executebuiltin('RunAddon(script.aw.gog.launcher)')
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Refresh("plugin://plugin.program.aw.gamelauncher")')
        elif (actionName == 'launchuplay'):
            xbmc.executebuiltin('RunAddon(script.aw.uplay.launcher)')
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Refresh("plugin://plugin.program.aw.gamelauncher")')
        elif (actionName == 'launchbattle'):
            xbmc.executebuiltin('RunAddon(script.aw.battle.launcher)')
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Refresh("plugin://plugin.program.aw.gamelauncher")')
        elif (actionName == 'findgames'):
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            findGames()
            xbmc.executebuiltin('Container.Refresh("plugin://plugin.program.aw.gamelauncher")')
        elif (actionName == 'games'):
            viewModeId = xbmc.getInfoLabel('Skin.String(GamesDefaultViewMode)')
            if (not viewModeId):
                xbmc.executebuiltin('Skin.SetString(GamesDefaultViewMode, %s)' % '500')
                xbmc.executebuiltin('Container.SetViewMode(%s)' % '500')

            xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)

            games = getGames()

            if (games):

                for game in games:
                    if (game.type == 0):
                        url = build_url(
                            {'mode': 'folder', 'action': 'addgame', 'gameid': game.gameId, 'gametype': game.type,
                             'gamepath': game.path})
                    else:
                        url = build_url(
                            {'mode': 'folder', 'action': 'launchgame', 'gameid': game.gameId, 'gametype': game.type,
                             'gamepath': game.path})
                    li = xbmcgui.ListItem(game.title, iconImage=game.thumbImage)
                    li.setProperty('Fanart_Image', game.fanartImage)

                    addContextMenu(game, li)
                    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=len(games),
                                                isFolder=False)
                xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

            if (not viewModeId):
                xbmc.executebuiltin('Container.SetViewMode(%s)' % '500')
        elif (actionName == 'launchgame'):
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            gameId = args['gameid'][0]
            gameType = args['gametype'][0]
            try:
                
                if (gameType == "1"):                    
                    steamExePath = getSteamExePath();                    

                    result = AlphaUIUtils.LaunchApplication(unicode(steamExePath), unicode(os.path.dirname(steamExePath)),unicode("-applaunch ") + unicode(gameId) + unicode(" -steamos -bigpicture"), True, False, True)

                    if not result:
                        customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
                        customizationAddonLanguage = customizationAddon.getLocalizedString
                        xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33020))

                elif (gameType == "2" or gameType == "4" or gameType == "5" or gameType == CUSTOM_GAME_TYPE):
                    gamePath = args['gamepath'][0]
                    #subprocess.Popen(gamePath, cwd=os.path.dirname(gamePath))
                    result = AlphaUIUtils.LaunchApplication(unicode(gamePath), unicode(os.path.dirname(gamePath)),unicode(""), True, False, True)
                    if not result:
                        customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
                        customizationAddonLanguage = customizationAddon.getLocalizedString
                        xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33020))
                elif (gameType == "3"):
                    gamePath = args['gamepath'][0]
                    cwd = gamePath.split(".exe", 1)[0] + ".exe"
                    #subprocess.Popen(gamePath, cwd=os.path.dirname(gamePath), shell=True)
                    result = AlphaUIUtils.LaunchApplication(unicode(gamePath), unicode(os.path.dirname(cwd)),unicode(""), True, False, True)
                    if not result:
                        customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
                        customizationAddonLanguage = customizationAddon.getLocalizedString
                        xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33020))
            except:
                pass


        elif (actionName == 'addgame'):
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

            games = getGameDictionary()

            gameId = 'Custom-%s' % getUuid()
            games[gameId] = {}
            games[gameId]['isNameChanged'] = 1
            games[gameId]['isPathChanged'] = 1
            games[gameId]['isIconChanged'] = 1
            games[gameId]['isFanartChanged'] = 1
            games[gameId]['type'] = CUSTOM_GAME_TYPE

            dialog = xbmcgui.Dialog()
            d = dialog.input(localize(33014), '', type=xbmcgui.INPUT_ALPHANUM)

            if (d):
                games[gameId]['name'] = d
                name = d

                d = dialog.browse(1, localize(33015), 'files', '.exe', True, False)
                if(d):
                    games[gameId]['path'] = d


                    thumbImage = os.path.join(DEFAULT_THUMB_PATH,"{0}_{1}.png".format(getSafeFileName(name), getUuid()))
                    if (not extractIcon(d, thumbImage)):
                        d = dialog.browse(2, localize(33016), 'files', '.png|.jpg', True, False)
                        #log(d)
                        if (d):
                            games[gameId]['thumbImage'] = d
                        else:
                            #set default icon
                            games[gameId]['thumbImage'] = "resources/skins/Default/media/alienware/battle.png"
                            #log("set default icon")
                    else:
                        #log(thumbImage)
                        games[gameId]['thumbImage'] = thumbImage
                    

                    prompt = dialog.yesno(localize(33022), localize(33023))
                    if (prompt):
                        d = dialog.browse(2, localize(33017), 'files', '.png|.jpg', True, False)
                        #log(d)
                    if (d and prompt):
                        games[gameId]['fanartImage'] = d
                    else:
                        #set default fanart
                        games[gameId]['fanartImage'] = "resources/skins/Default/media/alienware/fanart_battle.jpg"
                        #log("set default fanart")
                    writeToGameDB(games)

            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            url = build_url({'mode': 'folder', 'action': 'games'})
            xbmc.executebuiltin('Container.Refresh("' + url + '")')
    elif (mode[0] == 'context'):

        actionName = args['action'][0]
        menuActionName = ""

        games = getGames()
        gameId = args['gameid'][0]
        selectedGame = findSelectedGame(games, gameId)
        gamePath = selectedGame.path

        try:
            if (args['menuaction']):
                menuActionName = args['menuaction'][0]
        except:
            pass

        if (actionName == 'games'):

            games = getGames()

            if (menuActionName == 'addtofavorites'):
                if (games):
                    for game in games:
                        if (game.gameId == args['gameid'][0]):
                            addToFavorite(game)
                            break;
            elif (menuActionName == 'removefromfavorites'):
                if (games):
                    for game in games:
                        if (game.gameId == args['gameid'][0]):
                            removeFromFavorite(game)
                            break;
            elif (menuActionName == 'edittitle'):
                if (games):
                    for game in games:
                        if (game.gameId == args['gameid'][0]):
                            log(game.title)
                            log(game.path)
                            log(game.type)
                            dialog = xbmcgui.Dialog()
                            d = dialog.input(localize(33005), game.title, type=xbmcgui.INPUT_ALPHANUM)

                            if (d):
                                updateGameInformation(game, 'title', d)
                                break;
            elif (menuActionName == 'editicon'):
                if (games):
                    for game in games:
                        if (game.gameId == args['gameid'][0]):
                            dialog = xbmcgui.Dialog()
                            d = dialog.browse(2, localize(33007), 'files', '.jpg|.png', True, False, game.thumbImage)

                            if (d):
                                updateGameInformation(game, 'icon', d)
                                break;
            elif (menuActionName == 'editfanart'):
                if (games):
                    for game in games:
                        if (game.gameId == args['gameid'][0]):
                            dialog = xbmcgui.Dialog()
                            d = dialog.browse(2, localize(33008), 'files', '.jpg|.png', True, False, game.fanartImage)

                            if (d):
                                updateGameInformation(game, 'fanart', d)
                                break;
            elif (menuActionName == 'remove'):
                if (games):
                    for game in games:
                        if (game.gameId == args['gameid'][0]):
                            removeGame(game)
                   

            elif (menuActionName == 'addtogamesubmenu'):
                addtoHomeMenu(selectedGame, 'sub', gamePath)
            elif (menuActionName == 'removefromgamesubmenu'):
                removeFromHomeMenu(selectedGame, 'sub')
            elif (menuActionName == 'addtohomemenu'):
                addtoHomeMenu(selectedGame, 'home', gamePath)
            elif (menuActionName == 'removefromhomemenu'):
                removeFromHomeMenu(selectedGame, 'home')
 
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            url = build_url({'mode': 'folder', 'action': 'games'})
            xbmc.executebuiltin('Container.Refresh("' + url + '")')
            #log(url)

if (__name__ == "__main__"):
    # Addon paths creation
    if not os.path.exists(DEFAULT_THUMB_PATH): os.makedirs(DEFAULT_THUMB_PATH)
    if not os.path.exists(DEFAULT_FANART_PATH): os.makedirs(DEFAULT_FANART_PATH)

    games = {}
    isGameSave = True
    id = ''
    if (os.path.isfile(GAMES_DB_PATH)):
        gamesOrg = getGames()

        for game in gamesOrg:
            if (game.type == 0):
                isGameSave = False
                updateGameInformation(game, 'title', localize(33013))
                break;

        if (isGameSave):
            games = getGameDictionary()

    if (isGameSave):
        gameId = 'AddGame-%s' % getUuid()
        games[gameId] = {}
        games[gameId]['name'] = localize(33013)
        games[gameId]['path'] = ''
        games[gameId]['isNameChanged'] = 1
        games[gameId]['isPathChanged'] = 1
        games[gameId]['isIconChanged'] = 1
        games[gameId]['isFanartChanged'] = 1
        games[gameId]['type'] = 0
        games[gameId]['thumbImage'] = os.path.join(ADDONS_MEDIA_PATH, 'alienware', 'add.png')
        games[gameId]['fanartImage'] = ''
        isGameSave = True
        writeToGameDB(games)


