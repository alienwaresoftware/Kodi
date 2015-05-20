import xbmc

try:
    import AlphaUIUtils

    AlphaUIUtils.ShutdownSystem()
except:
    xbmc.executebuiltin('ShutDown')

