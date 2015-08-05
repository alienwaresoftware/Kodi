import xbmc
import xbmcgui
import os
import tempfile
import subprocess
import glob
import shutil
import string
import datetime
import time
import json
import traceback
import urllib
import urllib2
import urlparse
import AlphaUIUtils

from glob import glob
from xml.etree import ElementTree as ET

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

LOCAL_DATA_PATH = 'C:\ProgramData\Origin\LocalContent'
#RESOURCE_FILE = 'GDFBinary_en_US.dll'
RESOURCE_FILE = 'GDFBinary'
TEMP_DIR = tempfile.gettempdir()

class OriginGame(object):
    def __init__(self, defaultThumbPath, defaultFanartPath):
        self.defaultFanartPath = defaultFanartPath
        self.defaultThumbPath = defaultThumbPath

    def getMfstFiles(self):        
        mfstData = []
        if (os.path.exists(LOCAL_DATA_PATH)):                
            for game in os.listdir(LOCAL_DATA_PATH):                        
                gameFolderPath = os.path.join(LOCAL_DATA_PATH,game)
                if(os.path.exists(gameFolderPath)):                        
                    for file in os.listdir(gameFolderPath):
                        if file.endswith(".mfst"):
                            mfstPath = os.path.join(gameFolderPath,file)
                            file = open(mfstPath, 'r')
                            mfstData.append(file.read())
                            file.close()
        return mfstData

    def getGameInstallPath(self,data):

        queryStrings = urlparse.parse_qs(urllib.unquote(data))

        #log(queryStrings)
        if (len(queryStrings) > 0 and queryStrings.has_key('dipinstallpath')):
                return queryStrings.get('dipinstallpath')[0] 

    def extractDLL(self,installPath):
        if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
        #log("install path = " + installPath)

        newDllPath = ""
        dllPath = installPath
        filePath = ''

        for root, dir, files in os.walk(installPath):
                for file in files:
                        if file.startswith(RESOURCE_FILE):
                                log(file)
                                filePath = file
                                dllPath = (os.path.join(root, file))
                                newDllPath = os.path.join(TEMP_DIR,file)
                                shutil.copy2(dllPath, TEMP_DIR)

        resHackPath = os.path.join(__addonpath__,"resources","lib","ResourceHacker.exe")
        subprocess.call([resHackPath, "-extract", newDllPath, ",", "gameData.rc,", "DATA,,"])
        return filePath

    def parseXML(self,xmlPath,installPath, fileName):
        ns ={'gd': 'urn:schemas-microsoft-com:GameDescription.v1'}
        xmlTree = ET.parse(xmlPath)
        root = xmlTree.getroot()
        id = root.findall('.//gd:GameDefinition[@gameID]',ns)[0].attrib['gameID']
        id = string.replace(id,'{',"")
        id = string.replace(id,'}',"")
        name = root.findall('.//gd:GameDefinition/gd:Name',ns)[0].text
        primaryPath = os.path.join(installPath,root.findall('.//gd:Play/gd:Primary/gd:FileTask',ns)[0].attrib['path'])

        os.remove(TEMP_DIR + '\\' + "Data_1.bin")
        os.remove(TEMP_DIR + '\\' + "Data_2.bin")
        os.remove(TEMP_DIR + '\\' + "gameData.rc")
        os.remove(TEMP_DIR + '\\' + fileName)

        return name, id, primaryPath

    def findGames(self, orgGames, games):
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        isCanceled = False
        try:
            gameData = self.getMfstFiles()
            numFiles = len(gameData)
            if (numFiles > 0):
                counter = 0

                pDialog = xbmcgui.DialogProgress()
                pDialog.create(__addonname__, localize(33003))
                pDialog.update(0, localize(33003))

                for game in gameData:     
                    
                    try:           
                        installPath = self.getGameInstallPath(game)
                        #log("installPath = " + installPath)
                        fileName = self.extractDLL(installPath)                
                        xmlPath = os.path.join(TEMP_DIR,'Data_1.bin')
                        name, id, path = self.parseXML(xmlPath, installPath, fileName)

                        gameId = 'OR-%s' % id

                        orgGame = None

                        for game in orgGames:
                            if (game.gameId == gameId):
                                orgGame = game
                                break;

                        isNameChanged = 0
                        isPathChanged = 0
                        isIconChanged = 0
                        isFanartChanged = 0
                        thumbImage = ''
                        fanartImage = ''
                        type = 2

                        #log(path)
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


                    except:
                        log("error occured")

                pDialog.close()
        except Exception,e:
            #log(e.message)
            #log(e.__class__.__name__)
            traceback.print_exc(e)
        return games, isCanceled

    def extractIcon(self, filePath, extractIconPath):
        return AlphaUIUtils.GetIconFromExecutable(unicode(filePath), unicode(extractIconPath))

    def downloadGameImage(self,gameId, gameName,path):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        safeGameName = ''.join(c for c in gameName if c in valid_chars)
        findGameName = string.replace(safeGameName,' Demo','')

        #log('Downloading Origin game images for {0} -> {1}'.format(gameId, urllib.quote(safeGameName)))
    
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
                gameUrlQuery = {'exactname':findGameName.encode('utf8')}

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
                else:
                    screenshotNodes = root.findall('.//Game/Images/screenshot/original')
                    fanartImg = fanartNodes[0].text
                    thumbNodes = root.findall('.//Game/Images/screenshot/thumb')
                    thumbImg = thumbNodes[0].text

                downloadFile(baseImgUrl + fanartImg, fanartPath)
                downloadFile(baseImgUrl + thumbImg, thumbFilePath)
                isFanartFound = True
                isThumbImageFound = True
        except:
            pass

        #log(path)
        if(not isThumbImageFound):
            thumbFilePath = os.path.join(self.defaultThumbPath,'thumb_{0}_{1}.png'.format(safeGameName, int((time.mktime(datetime.datetime.now().timetuple())))))
            #log("extracting")
            #log(thumbFilePath)
            if(not self.extractIcon(path, thumbFilePath)):
               #log("failed")
               thumbFilePath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','origin.png')
        if(not isFanartFound):
            fanartPath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','fanart_origin.jpg')

        files.append(thumbFilePath)
        files.append(fanartPath)
    
        return files


