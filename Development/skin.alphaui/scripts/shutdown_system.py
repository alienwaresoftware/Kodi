import xbmc

try:
    import AlphaUIUtils

    if (not AlphaUIUtils.ShutdownSystem()):
        xbmc.executebuiltin('Powerdown')
except:
    xbmc.executebuiltin('Powerdown')

