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

class Uplay:
    def __init__(self, name, path, relative, registryKey, append):
        self.relative = relative
        self.registryKey = registryKey
        self.append = append
        self.name = name
        self.path = path
        self.gameId = ""

class UplayGame(object):
    def __init__(self, defaultThumbPath, defaultFanartPath):
        self.defaultFanartPath = defaultFanartPath
        self.defaultThumbPath = defaultThumbPath

    def getUuid(self):
        return uuid.uuid4().get_hex()
            
    def getInstallPath(self):
        installPath = ''
        try:
            if sys.maxsize > 2**32:
                arch_keys = {_winreg.KEY_WOW64_32KEY, _winreg.KEY_WOW64_64KEY}
            else:
                arch_keys = {_winreg.KEY_READ}

            for arch_key in arch_keys:
                key = None
                try:
                    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Ubisoft\Launcher', 0, _winreg.KEY_READ | arch_key)
                    installPath = _winreg.QueryValueEx(key, 'InstallDir')[0]
                except Exception,e:
                    pass
                finally:
                    if (key):
                        key.Close()
        except Exception,e:
            pass;

        if (not installPath):
            installPath = r'C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher'
        
        return installPath

    def getName(self, path):
        return string.replace(path, ".exe", "")

    def parseConfigurationFile(self):
        uplayPath = self.getInstallPath()
        if (uplayPath):
            configPath = os.path.join(uplayPath,r'cache\configuration\configurations')
            if (os.path.exists(configPath)):
                linesWanted = []
                uplayRegObjects = []
    
                file = open(configPath, 'rb')
                with open(configPath, 'rb') as f:
                    lines = f.readlines()        

                    for line in lines:            
                        line = line.rstrip()
                        if 'start_game:' in line or 'relative:' in line or 'register:' in line or 'append' in line:
                            if line not in linesWanted:
                                linesWanted.append(line)
                            elif 'start_game:' in line:
                                linesWanted.append(line)
                    
                    relative = ''
                    register = ''
                    append = ''
                    name = ''
                    haveRelative = False
                    haveRegister = False
                    haveName = False
                    for line in linesWanted:
                        if 'start_game' in line:
                            if haveRelative and haveRegister and haveName:
                                uplayRegObjects.append(Uplay(name, '', relative, register, append))
                                relative = ''
                                register = ''
                                append = ''
                                name = ''
                                haveRelative = False
                                haveRegister = False
                                haveName = False
                        elif 'relative' in line:
                            if haveRelative and haveRegister and haveName:
                                uplayRegObjects.append(Uplay(name, '', relative, register, append))
                                relative = ''
                                register = ''
                                append = ''
                                name = ''
                                haveRelative = False
                                haveRegister = False
                                haveName = False
                            relative = line.split(': ')[1]
                            name = self.getName(relative)
                            haveName = True
                            haveRelative = True
                        elif 'register' in line:
                            if haveRelative and haveRegister and haveName:
                                uplayRegObjects.append(Uplay(name, '', relative, register, append))
                                relative = ''
                                register = ''
                                append = ''
                                name = ''
                                haveRelative = False
                                haveRegister = False
                                haveName = False
                            register = string.replace(line.strip(),'register: ','')
                            register = string.replace(register,'"','')
                            register = string.replace(register,'\\\\','\\')
                            haveRegister = True


                        elif 'append' in line:
                            append = line.split(': ')[1]

                uplayGames = []
    
                for uplay in uplayRegObjects:
                    displayName = ''
                    try:
                        keyList = uplay.registryKey.split('\\')
                        keyType = keyList.pop(0)
                        value = keyList.pop(len(keyList) - 1)
                        subKey = '\\'.join(keyList)

                        keyType = _winreg.HKEY_LOCAL_MACHINE

                        if sys.maxsize > 2**32:
                            arch_keys = {_winreg.KEY_WOW64_32KEY, _winreg.KEY_WOW64_64KEY}
                        else:
                            arch_keys = {_winreg.KEY_READ}

                        for arch_key in arch_keys:
                            key = None
                            try:
                                key = _winreg.OpenKey(keyType, subKey, 0, _winreg.KEY_READ | arch_key)
                                installFolder = _winreg.QueryValueEx(key, value)[0]
                                uplay.path = os.path.join(installFolder, uplay.append, uplay.relative)
                                try:
                                    uplay.name = _winreg.QueryValueEx(key, 'DisplayName')[0]
                                except:
                                    pass
                                break
                            except Exception,e:
                                pass
                            finally:
                                if (key):
                                    key.Close()
                    except Exception,e:
                        pass;

                    if (uplay.path):
                        if (os.path.isfile(uplay.path)):
                            uplay.gameId = 'UP-{0}'.format(self.getUuid())
                            uplayGames.append(uplay)
                return uplayGames
    def extractIcon(self, filePath, extractIconPath):
        return AlphaUIUtils.GetIconFromExecutable(unicode(filePath), unicode(extractIconPath))

    def downloadGameImage(self,gameId, gameName, path):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        safeGameName = ''.join(c for c in gameName if c in valid_chars)
        aryGameName = safeGameName.split(" (Demo)")
        safeGameName = aryGameName[0].strip()

        #log('Downloading Uplay game images for {0} -> {1}'.format(gameId, urllib.quote(safeGameName)))
    
        files = []

        #valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        #safeGameName = ''.join(c for c in gameName if c in valid_chars)

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
                thumbFilePath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','uplay.png')
        if(not isFanartFound):
            fanartPath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','fanart_uplay.jpg')

        files.append(thumbFilePath)
        files.append(fanartPath)
    
        return files

    def findGames(self, orgGames, games):
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        isCanceled = False
        try:
            uplayGames = self.parseConfigurationFile()
            numFiles = len(uplayGames)
            if (numFiles > 0):
                counter = 0

                pDialog = xbmcgui.DialogProgress()
                pDialog.create(__addonname__, localize(33003))
                pDialog.update(0, localize(33003))

                for uplayGame in uplayGames:
                    orgGame = None
                    gameId = uplayGame.gameId
                    for game in orgGames:
                        if (game.gameId == gameId):
                            orgGame = game
                            break;

                    name = uplayGame.name
                    path = uplayGame.path
                    isNameChanged = 0
                    isPathChanged = 0
                    isIconChanged = 0
                    isFanartChanged = 0
                    thumbImage = ''
                    fanartImage = ''
                    type = 4

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