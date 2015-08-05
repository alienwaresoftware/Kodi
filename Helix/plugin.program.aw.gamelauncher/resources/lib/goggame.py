import xbmc
import xbmcgui
import os
import glob
import shutil
import string
import datetime
import tempfile
import subprocess
import time
import json
import traceback
import urllib
import urllib2
import urlparse
import sqlite3
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

DB_PATH = "C:\ProgramData\GOG.com\Galaxy\storage\index.db"
TEMP_DIR = tempfile.gettempdir()

class GogGame(object):
    def __init__(self, defaultThumbPath, defaultFanartPath):
        self.defaultFanartPath = defaultFanartPath
        self.defaultThumbPath = defaultThumbPath

    def findGameCount(self):
        gameCount = 0
        if (os.path.isfile(DB_PATH)):
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
        
            command = "SELECT count(*) from main.Products;"
            cur.execute(command)
            rowCount = cur.fetchone()
    
            con.close()
            gameCount = rowCount[0]

        return gameCount


    def extractDLL(self,installPath,dllFile):
        if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
        #log("install path = " + installPath)

        newDllPath = ""
        dllPath = installPath
        
        for root, dir, files in os.walk(installPath):
                for file in files:
                        if file.endswith(dllFile):
                                dllPath = (os.path.join(root, file))
                                newDllPath = os.path.join(TEMP_DIR,dllFile)
                                shutil.copy2(dllPath, TEMP_DIR)

        resHackPath = os.path.join(__addonpath__,"resources","lib","ResourceHacker.exe")
        subprocess.call([resHackPath, "-extract", newDllPath, ",", "gameData.rc,", "DATA,,"])

    def parseXML(self,xmlPath,installPath,dllFile):
        try:
            ns ={'gd': 'urn:schemas-microsoft-com:GameDescription.v1'}
            xmlTree = ET.parse(xmlPath)
            root = xmlTree.getroot()
            primaryPath = os.path.join(installPath,root.findall('.//gd:Play/gd:Primary/gd:FileTask',ns)[0].attrib['path'])
            arguments = root.findall('.//gd:Play/gd:Primary/gd:FileTask',ns)[0].attrib['arguments']
        except:
            arguments = ''
        os.remove(TEMP_DIR + '\\' + "Data_1.bin")
        os.remove(TEMP_DIR + '\\' + "Data_2.bin")
        os.remove(TEMP_DIR + '\\' + "gameData.rc")
        os.remove(TEMP_DIR + '\\' + dllFile)
        
        return primaryPath, arguments

    def findGames(self, orgGames, games):
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        isCanceled = False
        try:
            numFiles = self.findGameCount()
            if (numFiles > 0):
                counter = 0

                pDialog = xbmcgui.DialogProgress()
                pDialog.create(__addonname__, localize(33003))
                pDialog.update(0, localize(33003))

                con = sqlite3.connect(DB_PATH)
                cur = con.cursor()
    
                command = "SELECT productId, localpath from main.Products"
                cur.execute(command)
                rows = cur.fetchall()
                
                command ="SELECT productId, name from main.AvailableGameIDNames"
                cur.execute(command)
                allRows = cur.fetchall()    

                for row in rows:
                    id = row[0]
                    installPath = row[1]
                    name = ''

                    for i in allRows:
                        if id == i[0]:
                            name = i[1]
                            break

                    dllFile = 'goggame-%s.dll' % id
                    self.extractDLL(installPath, dllFile)
                    xmlPath = os.path.join(TEMP_DIR,'Data_2.bin')
                    path = ''
                    arguments = ''
                    path, arguments = self.parseXML(xmlPath,installPath,dllFile)

                    if arguments != '':
                        path = path + ' ' + arguments

                    gameId = 'GO-%s' % id
        
                    #find the shortcut link
                    #os.chdir(installPath)
                    #for file in glob("Launch*"):
                        #path = os.path.join(installPath, file)


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
                    type = 3

                    if ((not orgGame) or (orgGame is not None and orgGame.isFanartChanged == 0 and orgGame.isIconChanged == 0)):
                        gameFiles = self.downloadGameImage(gameId,name,os.path.join(installPath,"dummy.exe"))
                        thumbImage = gameFiles[0]
                        fanartImage = gameFiles[1]
                    elif (orgGame is not None and orgGame.isFanartChanged == 0):
                        gameFiles = self.downloadGameImage(gameId,name,os.path.join(installPath,"dummy.exe"))
                        thumbImage = orgGame.thumbImage
                        fanartImage = gameFiles[1]
                        isIconChanged = 1
                    elif (orgGame is not None and orgGame.isIconChanged == 0):
                        gameFiles = self.downloadGameImage(gameId,name,os.path.join(installPath,"dummy.exe"))
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
                con.close()
        except Exception,e:
            #log(e.message)
            #log(e.__class__.__name__)
            traceback.print_exc(e)
        return games, isCanceled

    def extractIcon(self, filePath, extractIconPath):
        return AlphaUIUtils.GetIconFromExecutable(unicode(filePath), unicode(extractIconPath))

    def downloadGameImage(self,gameId, gameName, path):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        safeGameName = ''.join(c for c in gameName if c in valid_chars)

        #log('Downloading GOG game images for {0} -> {1}'.format(gameId, urllib.quote(safeGameName)))
    
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
            if(not self.extractIcon(os.path.join(os.path.dirname(os.path.abspath(path)), string.replace("goggame-" + gameId + ".ico","-GO","")), thumbFilePath)):
                thumbFilePath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','gog.png')
        if(not isFanartFound):
            fanartPath = os.path.join(__addonpath__,'resources','skins','Default','media','alienware','fanart_gog.jpg')

        files.append(thumbFilePath)
        files.append(fanartPath)
    
        return files


