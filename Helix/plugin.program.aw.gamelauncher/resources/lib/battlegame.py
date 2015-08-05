import xbmc
import xbmcgui
import os
import urlparse
import urllib
import urllib2
import errno
import sys
import _winreg
import string
import traceback
import struct
import uuid
import time
import datetime
import json
import ntpath
import AlphaUIUtils

from glob import glob
from xml.etree import ElementTree as ET
from xml.dom import minidom

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


class Battle:       
        def __init__(self, id, name, exePath, installPath):
                self.name = name
                self.exePath = exePath
                self.gameId = id

class BattleGame(object):
    def __init__(self, defaultThumbPath, defaultFanartPath):
        self.defaultFanartPath = defaultFanartPath
        self.defaultThumbPath = defaultThumbPath

    def getUuid(self):
        return uuid.uuid4().get_hex()
            
    def getFilePath(self):
        return "C:\\ProgramData\\Battle.net\\Agent\\agent.db"

    def parseConfigurationFile(self):
        battleGames = []
        filePath = self.getFilePath()
        print filePath, os.path.isfile(filePath)
        if (filePath and os.path.isfile(filePath)):
            try:
                file = open(filePath, 'r')
                battleGameData = json.loads(file.read())

                gameData = []

                for battleGame in battleGameData:
                        if (string.find(battleGame,'/game/') == 0):
                                gameData.append(battleGameData[battleGame])


                for data in gameData:
                        #if (data['resource']['game']['download_complete']):
                                exePath = os.path.join(data['resource']['game']['install_dir'],data['resource']['game']['binary_launch_path'])
                                gamePath = data['resource']['game']['install_dir']
                                name = os.path.basename(gamePath)
                                if(name != "Battle.net"):
                                    #log(exePath + " " + gamePath + " "  + name)
                                    battleGames.append(Battle("BA-"+ self.getUuid(),name,exePath,gamePath))
            except Exception,e:
                #log(e.message)
                #log(e.__class__.__name__)
                traceback.print_exc(e)
        return battleGames

    def extractIcon(self, filePath, extractIconPath):
        return AlphaUIUtils.GetIconFromExecutable(unicode(filePath), unicode(extractIconPath))

    def downloadGameImage(self,gameId, gameName, path):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        safeGameName = ''.join(c for c in gameName if c in valid_chars)
        aryGameName = safeGameName.split(" (Demo)")
        safeGameName = aryGameName[0].strip()

        #log('Downloading Battle game images for {0} -> {1}'.format(gameId, urllib.quote(safeGameName)))
    
        files = []

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
                gameUrlQuery = {'exactname':safeGameName.encode('utf8')}

                requestURL = 'http://thegamesdb.net/api/GetGame.php?' + urllib.urlencode(gameUrlQuery)
    
                opener = urllib2.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]

                xmlResponse = opener.open(requestURL, timeout=30)

                strXml = xmlResponse.read()
                #log(strXml)
                root = ET.fromstring(strXml)
                baseImgUrl = root[0].text
                fanartNodes = root.findall('.//Game/Images/fanart/original')

                if (fanartNodes.count > 0):
                    fanartImg = fanartNodes[0].text
                    thumbNodes = root.findall('.//Game/Images/fanart/thumb')
                    thumbImg = thumbNodes[0].text

                downloadFile(baseImgUrl + fanartImg, fanartPath)
                downloadFile(baseImgUrl + thumbImg, thumbFilePath)
                isFanartFound = True
                isThumbImageFound = True
        except:
            pass

        if(not isThumbImageFound):
            thumbFilePath = os.path.join(self.defaultThumbPath,'thumb_{0}_{1}.png'.format(safeGameName, int((time.mktime(datetime.datetime.now().timetuple())))))
            if(not self.extractIcon(path, thumbFilePath)):
                thumbFilePath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','battle.png')
        if(not isFanartFound):
            fanartPath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','fanart_battle.jpg')

        files.append(thumbFilePath)
        files.append(fanartPath)
    
        return files

    def findGames(self, orgGames, games):
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        isCanceled = False
        try:
            battleGames = self.parseConfigurationFile()
            numFiles = len(battleGames)
            if (numFiles > 0):
                counter = 0

                pDialog = xbmcgui.DialogProgress()
                pDialog.create(__addonname__, localize(33003))
                pDialog.update(0, localize(33003))

                for battleGame in battleGames:
                    orgGame = None
                    gameId = battleGame.gameId
                    for game in orgGames:
                        if (game.gameId == gameId):
                            orgGame = game
                            break;

                    name = battleGame.name
                    path = battleGame.exePath
                    isNameChanged = 0
                    isPathChanged = 0
                    isIconChanged = 0
                    isFanartChanged = 0
                    thumbImage = ''
                    fanartImage = ''
                    type = 5

                    if ((not orgGame) or (orgGame is not None and orgGame.isFanartChanged == 0 and orgGame.isIconChanged == 0)):
                        gameFiles = self.downloadGameImage(gameId,name,path)
                        thumbImage = gameFiles[0]
                        fanartImage = gameFiles[1]
                    elif (orgGame is not None and orgGame.isFanartChanged == 0):
                        gameFiles = self.downloadGameImage(gameId,name,path)
                        thumbImage = orgGame.thumbImage
                        fanartImage = gameFiles[1]
                        isIconChanged = 1
                    elif (orgGame is not None and orgGame.isIconChanged == 0):
                        gameFiles = self.downloadGameImage(gameId,name,path)
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

                    if (pDialog.iscanceled()):
                        isCanceled = True
                        break;

                    pDialog.update(int((float(counter)/float(numFiles))*100), localize(33003))

                pDialog.close()
        except Exception,e:
            #log(e.message)
            #log(e.__class__.__name__)
            traceback.print_exc(e)
        return games, isCanceled