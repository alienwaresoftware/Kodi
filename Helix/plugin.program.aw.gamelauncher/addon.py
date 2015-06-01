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
from xml.etree import ElementTree as ET
from xml.dom import minidom
import urllib2
import traceback
import datetime
import time

from resources.lib.acf import *
import resources.lib.common as common
from resources.lib.common import log
from resources.lib.common import localize
from xml.dom.minidom import parse
from xml.dom.minidom import Document

__addon__        = common.__addon__
__addonid__ = common.__addonid__
__addonversion__ = common.__addonversion__
__addonname__    = common.__addonname__
__addonpath__    = common.__addonpath__
__icon__         = common.__icon__

# Addon paths definition
PLUGIN_DATA_PATH = xbmc.translatePath(os.path.join("special://profile/addon_data",__addonid__))
BASE_PATH = xbmc.translatePath(os.path.join("special://","profile"))
HOME_PATH = xbmc.translatePath(os.path.join("special://","home"))
FAVOURITES_PATH = xbmc.translatePath('special://profile/favourites.xml')
ADDONS_PATH = xbmc.translatePath(os.path.join(HOME_PATH,"addons"))
CURRENT_ADDON_PATH = xbmc.translatePath(os.path.join(ADDONS_PATH,__addonid__))
CURRENT_ADDON_LIB_PATH =  xbmc.translatePath(os.path.join(ADDONS_PATH,__addonid__,"resources","lib"))
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

def downloadFile(url, filePath):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    resource = opener.open(url, timeout=30)
    file = open(filePath,"wb")
    file.write(resource.read())
    file.close()

def downloadGameImage(gameId, gameName):
    log('Downloading Steam game images for {0} -> {1}'.format(gameId, gameName))
    
    files = []
    thumbFilePath = os.path.join(DEFAULT_THUMB_PATH,'thumb_{0}_{1}.jpg'.format(gameName, int((time.mktime(datetime.datetime.now().timetuple())))))
    fanartPath = os.path.join(DEFAULT_FANART_PATH,'fanart_{0}_{1}.jpg'.format(gameName, int((time.mktime(datetime.datetime.now().timetuple())))))

    for fileName in glob(os.path.join(DEFAULT_THUMB_PATH,'thumb_{0}*.*'.format(gameName))):
        os.remove(fileName)

    for fileName in glob(os.path.join(DEFAULT_FANART_PATH,'fanart_{0}*.*'.format(gameName))):
        os.remove(fileName)

    isFanartFound = False
    isThumbImageFound = False

    try:
        gameUrlQuery = {'exactname':gameName.encode('utf8')}

        requestURL = 'http://thegamesdb.net/api/GetGame.php?' + urllib.urlencode(gameUrlQuery)
    
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        xmlResponse = opener.open(requestURL, timeout=30)

        strXml = xmlResponse.read()

        root = ET.fromstring(strXml)
        baseImgUrl = root[0].text
        fanartNodes = root.findall('.//Game/Images/fanart/original')
        fanartImg = fanartNodes[0].text

        downloadFile(baseImgUrl + fanartImg, fanartPath)
        isFanartFound = True
    except:
        pass

    try:
        response = urllib.urlopen('http://store.steampowered.com/api/appdetails?appids={0}'.format(gameId))
        gameJason = json.loads(response.read())
        response.close()

        if(not isThumbImageFound):
            downloadFile(gameJason[gameId]['data']['header_image'], thumbFilePath)
            isThumbImageFound = True

        if(not isFanartFound):
            downloadFile(gameJason[gameId]['data']['screenshots'][0]['path_full'], fanartPath)
            isFanartFound = True    

    except:
        pass    

    if(not isThumbImageFound):
        thumbFilePath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','steam.png')
    if(not isFanartFound):
        fanartPath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','fanart_steam.png')

    files.append(thumbFilePath)
    files.append(fanartPath)
    
    return files

def findGames():
    steamPath = getSteamPath()
    steamAppPath = os.path.join(os.path.abspath(steamPath),'steamapps')

    games = {}

    files = glob('{0}/*.acf'.format(steamAppPath))
    numFiles = len(files)
    counter = 0

    pDialog = xbmcgui.DialogProgress()
    pDialog.create(__addonname__, localize(33003))
    pDialog.update(0, localize(33003))

    for filePath in glob('{0}/*.acf'.format(steamAppPath)):
        gameDict = parse_acf(filePath)
        if (gameDict['AppState']['BytesToDownload'] != '0' and gameDict['AppState']['BytesToDownload'] == gameDict['AppState']['BytesDownloaded']):
            gameFiles = downloadGameImage(gameDict['AppState']['appid'],gameDict['AppState']['name'])
            games[gameDict['AppState']['appid']] = {}
            games[gameDict['AppState']['appid']]['name'] = gameDict['AppState']['name']
            games[gameDict['AppState']['appid']]['type'] = 1
            games[gameDict['AppState']['appid']]['thumbImage'] = gameFiles[0]
            games[gameDict['AppState']['appid']]['fanartImage'] = gameFiles[1]
            counter = counter + 1
            pDialog.update(int((float(counter)/float(numFiles))*100), localize(33003))

    gamesDbObj = open(GAMES_DB_PATH, 'w')
    gamesDbObj.write(json.dumps(games))
    gamesDbObj.close()
    pDialog.close()
    dialog = xbmcgui.Dialog()
    ok = dialog.ok(__addonname__, str(numFiles) + ' ' + localize(33004))
    
def getGames():
    games = []

    if (not os.path.isfile(GAMES_DB_PATH)):
        return games

    gamesDbfile = open(GAMES_DB_PATH,'r')
    gamesJson = json.loads(gamesDbfile.read())
    gamesDbfile.close()

    for game in gamesJson:
        games.append(Game(game, gamesJson[game]['name'], gamesJson[game]['type'], gamesJson[game]['thumbImage'], gamesJson[game]['fanartImage']))

    return games    

def isInFavorites(game):
    if os.path.isfile( FAVOURITES_PATH ):
        fav_xml = parse( FAVOURITES_PATH )
        fav_doc = fav_xml.documentElement.getElementsByTagName( 'favourite' )
        for count, favourite in enumerate(fav_doc):
            if (favourite.attributes['name'].nodeValue == game.title and favourite.firstChild.data == getGameLaunchUrlAction(game)):
                return True
    else:
        return False

def getGameLaunchUrlAction(game):
    return 'PlayMedia("{0}")'.format(build_url({'mode': 'folder', 'action': 'launchgame', 'gameid': game.gameId, 'gametype': game.type}))

def addContextMenu(game,listItem):
    #ActivateWindow(10001,&quot;plugin://plugin.program.aw.gamelauncher/?action=addtofavorite&amp;mode=folder&quot;,return)

    menuTuple = None

    if (isInFavorites(game)):
       menuTuple = (xbmc.getLocalizedString(14077), 'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=removefromfavorites&amp;mode=folder&amp;gameid={0})'.format(game.gameId),)
    else:
       menuTuple = (xbmc.getLocalizedString(14076), 'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=addtofavorites&amp;mode=folder&amp;gameid={0})'.format(game.gameId),)

    listItem.addContextMenuItems([menuTuple,
                                    (localize(33005), 'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=edittitle&amp;mode=folder&amp;gameid={0})'.format(game.gameId),),
                                    (localize(33006), 'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=editpath&amp;mode=folder&amp;gameid={0})'.format(game.gameId),),
                                    (localize(33007), 'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=editicon&amp;mode=folder&amp;gameid={0})'.format(game.gameId),),
                                    (localize(33008), 'XBMC.Container.Refresh(plugin://plugin.program.aw.gamelauncher/?action=games&amp;menuaction=editfanart&amp;mode=folder&amp;gameid={0})'.format(game.gameId),),],True)

def addToFavorite(game):
    doc = None
    root = None

    log('add to favorite ' + game.title)

    if (not os.path.isfile(FAVOURITES_PATH)):            
        doc = Document()
        root = doc.createElement("favourites")
        doc.appendChild(root)
    else:
        doc = parse( FAVOURITES_PATH )
        root = doc.documentElement

    favNode = doc.createElement("favourite")
    root.appendChild(favNode)

    favNode.setAttribute( "name", game.title)
    favNode.setAttribute( "thumb", game.thumbImage)

    url = getGameLaunchUrlAction(game)

    textNode = doc.createTextNode(url)
    favNode.appendChild(textNode)
 
    doc.writexml(open(FAVOURITES_PATH, 'w'))
 
    doc.unlink()

def removeFromFavorite(game):
    if os.path.isfile( FAVOURITES_PATH ):
        doc = parse( FAVOURITES_PATH )
        fav_doc = doc.documentElement.getElementsByTagName('favourite')
        for count, favourite in enumerate(fav_doc):
            if (favourite.attributes['name'].nodeValue == game.title and favourite.firstChild.data == getGameLaunchUrlAction(game)):
                doc.documentElement.removeChild(favourite)
                break;

    doc.writexml(open(FAVOURITES_PATH, 'w'))
 
    doc.unlink()


mode = args.get('mode', None)
log(args)
if mode is None:
    imageFilePath = os.path.join(CURRENT_ADDON_PATH, 'resources','skins','Default','media','alienware')

    url = build_url({'mode': 'folder', 'action': 'games'})
    #print "url -> {0}".format(url)
    li = xbmcgui.ListItem(localize(33000), iconImage=os.path.join(imageFilePath, 'games.png'))
    #log(os.path.join(imageFilePath, 'games.png'))
    #li.setProperty('Fanart_Image', os.path.join(CURRENT_ADDON_PATH, 'fanart.jpg'))
    #log(os.path.join(CURRENT_ADDON_PATH, 'fanart.jpg'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'action': 'findgames'})
    li = xbmcgui.ListItem(localize(33001), iconImage=os.path.join(imageFilePath, 'findgames.png'))
    #li.setProperty('Fanart_Image', os.path.join(CURRENT_ADDON_PATH, 'fanart.jpg'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)
    
    url = build_url({'mode': 'folder', 'action': 'steam'})
    li = xbmcgui.ListItem(localize(33002), iconImage=os.path.join(imageFilePath, 'steam.png'))
    #li.setProperty('Fanart_Image', os.path.join(CURRENT_ADDON_PATH, 'fanart.jpg'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

elif (mode[0] == 'folder'):    
    actionName = args['action'][0]

    menuActionName = ""
    try:
        if (args['menuaction']):
            menuActionName = args['menuaction'][0]
    except:
        pass

    if (actionName == 'steam'):
        try:
            AlphaUIUtils.LaunchSteam()
        except:
            pass
    elif (actionName == 'findgames'):
        findGames()
    elif (actionName == 'games'):
        games = getGames()

        if (menuActionName == 'addtofavorites'):
            log('add to favorite ' + args['gameid'][0])

            if (games):
                for game in games:
                    if (game.gameId == args['gameid'][0]):
                        log('game found')
                        addToFavorite(game)
                        break;
        elif (menuActionName == 'removefromfavorites'):
            if (games):
                for game in games:
                    if (game.gameId == args['gameid'][0]):
                        removeFromFavorite(game)
                        break;
        if (games):
            for game in games:
                url = build_url({'mode': 'folder', 'action': 'launchgame', 'gameid': game.gameId, 'gametype': game.type})
                li = xbmcgui.ListItem(game.title, iconImage=game.thumbImage)
                li.setProperty('Fanart_Image', game.fanartImage)
                addContextMenu(game,li)
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)    
    elif (actionName == 'launchgame'):
        gameId = args['gameid'][0]
        gameType = args['gametype'][0]

        if (gameType == "1"):
            AlphaUIUtils.LaunchSteamGame(unicode(gameId))
