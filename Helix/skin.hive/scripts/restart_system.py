import xbmc

try:
    import AlphaUIUtils

    AlphaUIUtils.RestartSystem()
except:
    xbmc.executebuiltin('Reboot')
