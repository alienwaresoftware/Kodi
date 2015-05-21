import xbmc

try:
    import AlphaUIUtils

    AlphaUIUtils.SleepSystem()
except:
    xbmc.executebuiltin('Suspend')
