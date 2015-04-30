import xbmc
import xbmcgui
import xbmcaddon
import sys

ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

__scriptID__   = 'script.module.aw.devicesettings'
__addon__ = xbmcaddon.Addon(id=__scriptID__)

class DeviceSettingsWindow(xbmcgui.WindowXML):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback=True):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.isClosed = False

    def isComplete(self): 
        return self.isClosed 

    def onAction(self, action):
        if (action.getId() == ACTION_PREVIOUS_MENU or action.getId() == ACTION_NAV_BACK ):
            self.close()

    def close(self):
        self.isClosed = True 
        xbmcgui.WindowXML.close(self)    

deviceSettingsWindow = DeviceSettingsWindow("awdevicesettings.xml",__addon__.getAddonInfo('path'), "Default")
deviceSettingsWindow.show()
monitor = xbmc.Monitor()
while not deviceSettingsWindow.isComplete(): 
    if monitor.waitForAbort(2):
        # Abort was requested while waiting. We should exit
        break
    if (xbmcgui.getCurrentWindowId() == 10000):
        break

del deviceSettingsWindow
