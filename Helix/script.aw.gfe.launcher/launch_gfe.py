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

__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__addonpath__    = __addon__.getAddonInfo('path').decode('utf-8')
__addonprofile__ = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode('utf-8')
__icon__         = __addon__.getAddonInfo('icon')
__customizationaddon__ = xbmcaddon.Addon(id='service.aw.customizations')
__customizationaddonlanguage__ = __customizationaddon__.getLocalizedString

def readRegistryValue(subKey, itemName):
        value = ''

        try:
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, subKey, 0, _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY)
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

            exePath = readRegistryValue(r'SOFTWARE\NVIDIA Corporation\Global\GFEClient', 'FullPath')
            launchPath = exePath

            if (not os.path.isfile(launchPath)):
                if (xbmcgui.Dialog().yesno(__addonname__,__customizationaddonlanguage__(33021),'',__customizationaddonlanguage__(33022))):
                    webbrowser.open('http://www.geforce.com/geforce-experience')
            else:
                #subprocess.Popen(launchPath,cwd=os.path.dirname(launchPath))
                result = AlphaUIUtils.LaunchApplication(unicode(launchPath), unicode(os.path.dirname(launchPath)),unicode(""), True, False, True)
                if not result:
                    customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
                    customizationAddonLanguage = customizationAddon.getLocalizedString
                    xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33020))
        except:
               pass

