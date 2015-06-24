import xbmc

try:
    import AlphaUIUtils

    if (not AlphaUIUtils.SleepSystem()):
        xbmc.executebuiltin('Suspend')
except:
    xbmc.executebuiltin('Suspend')
