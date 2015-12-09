import xbmc
import xbmcgui
import os
import sys
import string
import datetime
import time
import json
import traceback
import urllib
import urllib2

from glob import glob
from _winreg import *
from xml.etree import ElementTree as ET
from xml.dom import minidom
from acf import *

import common as common
from common import log
from common import localize
from common import downloadFile

__addon__        = common.__addon__
__addonid__ = common.__addonid__
__addonversion__ = common.__addonversion__
__addonname__    = common.__addonname__
__addonpath__    = common.__addonpath__
__icon__         = common.__icon__

class SteamGame(object):
    def __init__(self, defaultThumbPath, defaultFanartPath):
        self.defaultFanartPath = defaultFanartPath
        self.defaultThumbPath = defaultThumbPath

    # Fixes unicode problems
    def getSteamPath(self):
        import errno, sys, _winreg
        steamPath = ''

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
        except Exception,e:
            log(e.message)
            log(e.__class__.__name__)
            traceback.print_exc(e)
        return steamPath

    def downloadGameImage(self,gameId, gameName):
        log('Downloading Steam game images for {0} -> {1}'.format(gameId, gameName))
    
        files = []

        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        safeGameName = ''.join(c for c in gameName if c in valid_chars)

        thumbFilePath = os.path.join(self.defaultThumbPath,'thumb_{0}_{1}.jpg'.format(safeGameName, int((time.mktime(datetime.datetime.now().timetuple())))))
        fanartPath = os.path.join(self.defaultFanartPath,'fanart_{0}_{1}.jpg'.format(safeGameName, int((time.mktime(datetime.datetime.now().timetuple())))))

        isFanartFound = False
        isThumbImageFound = False

        for fileName in glob(os.path.join(self.defaultThumbPath,'thumb_{0}*.*'.format(safeGameName))):
            thumbFilePath = fileName
            isThumbImageFound = True

        for fileName in glob(os.path.join(self.defaultFanartPath,'fanart_{0}*.*'.format(safeGameName))):
            fanartPath = fileName
            isFanartFound = True

        try:
            if (not isFanartFound):
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
            if (not isThumbImageFound or not isFanartFound):
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

    def findGames(self, orgGames, games):
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        isCanceled = False
        try:
            steamPath = self.getSteamPath()
            if (steamPath):
                steamAppPath = os.path.join(os.path.abspath(steamPath),'steamapps')

                files = glob('{0}/*.acf'.format(steamAppPath))
                numFiles = len(files)
                if (numFiles > 0):
                    counter = 0

                    pDialog = xbmcgui.DialogProgress()
                    pDialog.create(__addonname__, localize(33003))
                    pDialog.update(0, localize(33003))

                    for filePath in glob('{0}/*.acf'.format(steamAppPath)):
                        log('findGames()::filepath -> %s' % filePath)
                        #try:
                        gameDict = parse_acf(filePath)

                        #if (gameDict['appstate']['bytestodownload'] != '0' and gameDict['appstate']['bytestodownload'] == gameDict['appstate']['bytesdownloaded']):
                        if(True):
                            orgGame = None
                            gameId = gameDict['appstate']['appid']
                            for game in orgGames:
                                if (game.gameId == gameId):
                                    orgGame = game
                                    break;

                            name = gameDict['appstate']['name']
                            path = ''
                            isNameChanged = 0
                            isPathChanged = 0
                            isIconChanged = 0
                            isFanartChanged = 0
                            thumbImage = ''
                            fanartImage = ''
                            type = 1

                            if ((not orgGame) or (orgGame is not None and orgGame.isFanartChanged == 0 and orgGame.isIconChanged == 0)):
                                gameFiles = self.downloadGameImage(gameId,gameDict['appstate']['name'])
                                thumbImage = gameFiles[0]
                                fanartImage = gameFiles[1]
                            elif (orgGame is not None and orgGame.isFanartChanged == 0):
                                gameFiles = self.downloadGameImage(gameId,gameDict['appstate']['name'])
                                thumbImage = orgGame.thumbImage
                                fanartImage = gameFiles[1]
                                isIconChanged = 1
                            elif (orgGame is not None and orgGame.isIconChanged == 0):
                                gameFiles = self.downloadGameImage(gameId,gameDict['appstate']['name'])
                                thumbImage = gameFiles[0]
                                fanartImage = orgGame.fanartImage
                                isFanartChanged = 1
                            else:
                                thumbImage = orgGame.thumbImage
                                fanartImage = orgGame.fanartImage
                                isIconChanged = 1
                                isFanartChanged = 1

                            if (orgGame is not None and orgGame.isNameChanged == 1):
                                name = orgGame.title
                                isNameChanged = 1

                            if (orgGame is not None and orgGame.isPathChanged == 1):
                                name = orgGame.path
                                isPathChanged = 1

                            games[gameId] = {}
                            games[gameId]['name'] = name
                            games[gameId]['path'] = path
                            games[gameId]['isNameChanged'] = isNameChanged
                            games[gameId]['isPathChanged'] = isPathChanged
                            games[gameId]['isIconChanged'] = isIconChanged
                            games[gameId]['isFanartChanged'] = isFanartChanged
                            games[gameId]['type'] = type
                            games[gameId]['thumbImage'] = thumbImage
                            games[gameId]['fanartImage'] = fanartImage

                            counter = counter + 1
                        #except:
                            #log('unable to parse the file %s' % filePath)

                        if (pDialog.iscanceled()):
                            isCanceled = True
                            break;

                        pDialog.update(int((float(counter)/float(numFiles))*100), localize(33003))

                    pDialog.close()
        except Exception,e:
            log(e.message)
            log(e.__class__.__name__)
            traceback.print_exc(e)
        return games, isCanceled
