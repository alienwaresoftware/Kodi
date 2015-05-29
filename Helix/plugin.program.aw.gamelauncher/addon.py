import os
import sys
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
from glob import glob
from _winreg import *
import json
import subprocess
import AlphaUIUtils

from resources.lib.acf import *
import resources.lib.common as common
from resources.lib.common import log

__addon__        = common.__addon__
__addonid__ = common.__addonid__
__addonversion__ = common.__addonversion__
__addonname__    = common.__addonname__
__addonpath__    = common.__addonpath__
__icon__         = common.__icon__

print __addon__
print __addonversion__
print __addonid__
print __addonpath__
print __icon__

# Addon paths definition
PLUGIN_DATA_PATH = xbmc.translatePath(os.path.join("special://profile/addon_data",__addonid__))
BASE_PATH = xbmc.translatePath(os.path.join("special://","profile"))
HOME_PATH = xbmc.translatePath(os.path.join("special://","home"))
FAVOURITES_PATH = xbmc.translatePath( 'special://profile/favourites.xml' )
ADDONS_PATH = xbmc.translatePath(os.path.join(HOME_PATH,"addons"))
CURRENT_ADDON_PATH = xbmc.translatePath(os.path.join(ADDONS_PATH,__addonid__))
GAMES_DB_PATH = os.path.join(PLUGIN_DATA_PATH,"games.db")
DEFAULT_THUMB_PATH = os.path.join(PLUGIN_DATA_PATH,"thumbs")
DEFAULT_FANART_PATH = os.path.join(PLUGIN_DATA_PATH,"fanarts")

log(CURRENT_ADDON_PATH)

# Addon paths creation
if not os.path.exists(DEFAULT_THUMB_PATH): os.makedirs(DEFAULT_THUMB_PATH)
if not os.path.exists(DEFAULT_FANART_PATH): os.makedirs(DEFAULT_FANART_PATH)


class Game(object):
    def __init__(self, gameId, title, type, thumbImage, fanartImage):
        self.gameId = gameId
        self.title = title
        self.type = type
        self.thumbImage = thumbImage
        self.fanartImage = fanartImage

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'games')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def getSteamPath():
    import errno, sys, _winreg
    steamPath = ""

    try:
        if sys.maxsize > 2**32:
            arch_keys = {_winreg.KEY_WOW64_32KEY, _winreg.KEY_WOW64_64KEY}
        else:
            arch_keys = {_winreg.KEY_READ}

        for arch_key in arch_keys:

            print "reading"
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", 0, _winreg.KEY_READ | arch_key)
            try:
                steamPath = _winreg.QueryValueEx(key, 'InstallPath')[0]
            except OSError as e:
                if e.errno == errno.ENOENT:
                    # DisplayName doesn't exist in this skey
                    pass
            finally:
                key.Close()
    except:
        pass
    return steamPath

def downloadGameImage(gameId):
    files = []
    thumbFilePath = os.path.join(DEFAULT_THUMB_PATH,'thumb_{0}.jpg'.format(gameId))
    files.append(thumbFilePath)
    fanartPath = os.path.join(DEFAULT_FANART_PATH,'fanart_{0}.jpg'.format(gameId))
    files.append(fanartPath)

    if (os.path.isfile(thumbFilePath) and os.path.isfile(fanartPath)):
         return files

    response = urllib.urlopen('http://store.steampowered.com/api/appdetails?appids={0}'.format(gameId))
    gameJason = json.loads(response.read())
    response.close()
    urllib.urlretrieve(gameJason[gameId]['data']['header_image'], thumbFilePath)
    urllib.urlretrieve(gameJason[gameId]['data']['screenshots'][0]['path_full'], fanartPath)
    return files

def findGames():
    steamPath = getSteamPath()
    steamAppPath = os.path.join(os.path.abspath(steamPath),'steamapps')

    games = {}

    files = glob('{0}/*.acf'.format(steamAppPath))
    numFiles = len(files)
    log(numFiles)
    counter = 0

    pDialog = xbmcgui.DialogProgress()
    pDialog.create("Game Finder", "Finding Games....")
    pDialog.update(0, "Finding Games....")

    for filePath in glob('{0}/*.acf'.format(steamAppPath)):
        gameDict = parse_acf(filePath)
        log(gameDict)
        if (gameDict['AppState']['BytesToDownload'] != '0' and gameDict['AppState']['BytesToDownload'] == gameDict['AppState']['BytesDownloaded']):
            gameFiles = downloadGameImage(gameDict['AppState']['appid'])
            games[gameDict['AppState']['appid']] = {}
            games[gameDict['AppState']['appid']]['name'] = gameDict['AppState']['name']
            games[gameDict['AppState']['appid']]['type'] = 1
            games[gameDict['AppState']['appid']]['thumbImage'] = gameFiles[0]
            games[gameDict['AppState']['appid']]['fanartImage'] = gameFiles[1]
            counter = counter + 1
            pDialog.update(int((float(counter)/float(numFiles))*100), "Finding Games")

    gamesDbObj = open(GAMES_DB_PATH, 'w')
    gamesDbObj.write(json.dumps(games))
    gamesDbObj.close()
    pDialog.close()
    
def getGames():
    games = []

    if (not os.path.isfile(GAMES_DB_PATH)):
        return games

    gamesDbfile = open(GAMES_DB_PATH,'r')
    gamesJson = json.loads(gamesDbfile.read())
    gamesDbfile.close()

    for game in gamesJson:
        log(game)
        games.append(Game(game, gamesJson[game]['name'], gamesJson[game]['type'], gamesJson[game]['thumbImage'], gamesJson[game]['fanartImage']))

    return games    

mode = args.get('mode', None)
log("Starting")

if mode is None:
    imageFilePath = os.path.join(CURRENT_ADDON_PATH, 'resources','skins','Default','media','alienware')

    url = build_url({'mode': 'folder', 'action': 'games'})
    #print "url -> {0}".format(url)
    li = xbmcgui.ListItem('Games', iconImage=os.path.join(imageFilePath, 'games.png'))
    #log(os.path.join(imageFilePath, 'games.png'))
    li.setProperty('Fanart_Image', os.path.join(CURRENT_ADDON_PATH, 'fanart.jpg'))
    #log(os.path.join(CURRENT_ADDON_PATH, 'fanart.jpg'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'action': 'findgames'})
    li = xbmcgui.ListItem('Find Games', iconImage=os.path.join(imageFilePath, 'findgames.png'))
    li.setProperty('Fanart_Image', os.path.join(CURRENT_ADDON_PATH, 'fanart.jpg'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)
    
    url = build_url({'mode': 'folder', 'action': 'steam'})
    li = xbmcgui.ListItem('Launch Steam', iconImage=os.path.join(imageFilePath, 'steam.png'))
    li.setProperty('Fanart_Image', os.path.join(CURRENT_ADDON_PATH, 'fanart.jpg'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif (mode[0] == 'folder'):
    actionName = args['action'][0]
    print "actionName -> {0}".format(actionName)

    if (actionName == 'steam'):
        try:
            AlphaUIUtils.LaunchSteam()
        except:
            pass
    elif (actionName == 'findgames'):
        findGames()
    elif (actionName == 'games'):
        games = getGames()
        if (games):
            for game in games:
                url = build_url({'mode': 'folder', 'action': 'launchgame', 'gameid': game.gameId, 'gametype': game.type})
                print url
                li = xbmcgui.ListItem(game.title, iconImage=game.thumbImage)
                li.setProperty('Fanart_Image', game.fanartImage)
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
            xbmcplugin.endOfDirectory(addon_handle)    
    elif (actionName == 'launchgame'):
        gameId = args['gameid'][0]
        gameType = args['gametype'][0]

        if (gameType == "1"):
            AlphaUIUtils.LaunchSteamGame(unicode(gameId))
