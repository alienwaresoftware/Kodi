import xbmc
import xbmcgui
import xbmcaddon


__scriptID__   = 'script.aw.steam.launcher'
__addon__ = xbmcaddon.Addon(id=__scriptID__)
__addonname__ = __addon__.getAddonInfo('name')

if (__name__ == "__main__"):
    if (xbmcgui.Window(10004).getProperty('service.aw.customizations.isComponentInstalled') == "False"):
        customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
        customizationAddonLanguage = customizationAddon.getLocalizedString

        xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33011))
    else:
        import AlphaUIUtils

        AlphaUIUtils.LaunchSteam()
