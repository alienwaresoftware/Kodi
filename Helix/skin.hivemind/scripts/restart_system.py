import xbmc

try:
    import AlphaUIUtils

    if (not AlphaUIUtils.RestartSystem()):
        xbmc.executebuiltin('Reboot')
except:
    xbmc.executebuiltin('Reboot')
