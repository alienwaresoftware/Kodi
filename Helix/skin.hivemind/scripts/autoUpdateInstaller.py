import xbmcgui
import AlphaUIAutoUpdate
from AlphaUIAutoUpdate import AutoUpdateClass

autoUpdateClass = AutoUpdateClass(xbmcgui.Window(xbmcgui.getCurrentWindowId()))
autoUpdateClass.showMessageAndLaunchUpdates()