import xbmc
import xbmcgui
import xbmcaddon
import os
import errno
import sys
import _winreg
import webbrowser
import subprocess
import traceback
import time
import json
import string

__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__addonpath__    = __addon__.getAddonInfo('path').decode('utf-8')
__addonprofile__ = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode('utf-8')
__icon__         = __addon__.getAddonInfo('icon')
__customizationaddon__ = xbmcaddon.Addon(id='service.aw.customizations')
__customizationaddonlanguage__ = __customizationaddon__.getLocalizedString



def getUuid():
    return uuid.uuid4().get_hex()
            
def getFilePath():
    return "C:\\ProgramData\\Battle.net\\Agent\\agent.db"

def parseConfigurationFile():
    battleGames = []
    filePath = getFilePath()
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
                            if(name == "Battle.net"):
                                #log(exePath + " " + gamePath + " "  + name)
                                #battleGames.append(Battle("BA-"+ self.getUuid(),name,exePath,gamePath))
								return name, exePath, gamePath
								
        except Exception,e:
            #log(e.message)
            #log(e.__class__.__name__)
            traceback.print_exc(e)
    return "","",""


def readRegistryValue(subKey, itemName):
        value = ''

        try:
            if sys.maxsize > 2**32:
                arch_keys = {_winreg.KEY_WOW64_32KEY, _winreg.KEY_WOW64_64KEY}
            else:
                arch_keys = {_winreg.KEY_READ}

            for arch_key in arch_keys:

                key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, subKey, 0, _winreg.KEY_READ | arch_key)
                try:
                    value = _winreg.QueryValueEx(key, itemName)[0]
                except OSError as e:
                    if e.errno == errno.ENOENT:
                        pass
                finally:
                    key.Close()
        except Exception,e:
            #log(e.message)
            #log(e.__class__.__name__)
            traceback.print_exc(e)
        return value

def log(txt):
    if isinstance (txt,str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonname__, txt)
    #xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)
    print(message.encode("utf-8"))

if (__name__ == "__main__"):
    if (xbmcgui.Window(10004).getProperty('service.aw.customizations.isComponentInstalled') == "False"):
        xbmcgui.Dialog().ok(__addonname__, __customizationaddonlanguage__(33011))
    else:
        import AlphaUIUtils
        try:

            name, exePath, gamePath = parseConfigurationFile()

            launchPath = exePath.replace('/','\\')

            #if (not exeName or not exePath or not os.path.isfile(launchPath)):
            if(not os.path.isfile(launchPath)):
                if (xbmcgui.Dialog().yesno(__addonname__,__customizationaddonlanguage__(33018),'',__customizationaddonlanguage__(33019))):
                    webbrowser.open('http://www.battle.net')
            else:
                
                #subprocess.Popen(launchPath,cwd=os.path.dirname(launchPath))
                log(launchPath)
                log(os.path.dirname(launchPath))
                result = AlphaUIUtils.LaunchApplication(unicode(launchPath), unicode(os.path.dirname(launchPath)),unicode(""), True, False, False)
                if not result:
                    customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
                    customizationAddonLanguage = customizationAddon.getLocalizedString
                    xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33020))
        except:
               pass


