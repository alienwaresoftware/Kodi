import os
import xbmc
import xbmcgui
import xbmcaddon


__scriptID__   = 'script.aw.steam.launcher'
__addon__ = xbmcaddon.Addon(id=__scriptID__)
__addonname__ = __addon__.getAddonInfo('name')

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

if (__name__ == "__main__"):
    if (xbmcgui.Window(10004).getProperty('service.aw.customizations.isComponentInstalled') == "False"):
        customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
        customizationAddonLanguage = customizationAddon.getLocalizedString

        xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33011))
    else:
        import AlphaUIUtils

        steamExePath = getSteamExePath();                    

        result = AlphaUIUtils.LaunchApplication(unicode(steamExePath), unicode(os.path.dirname(steamExePath)),unicode("steam://open/bigpicture"), True, False, False)

        if not result:
            customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
            customizationAddonLanguage = customizationAddon.getLocalizedString
            xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33020))
