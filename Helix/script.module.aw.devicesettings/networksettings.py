import xbmc
import xbmcgui
import xbmcaddon
import sys
import dialogselect

from resources.lib.wirelessnetwork import WiFiHelper

WIFI_LIST_CONTROL = 106

ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

ACTION_MOUSE_LEFT_CLICK = 100
ACTION_MOUSE_DRAG = 106

__scriptID__   = 'script.module.aw.devicesettings'
__addon__ = xbmcaddon.Addon(id=__scriptID__)
__language__ = __addon__.getLocalizedString

class NetworkSettingsWindow(xbmcgui.WindowXML):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback=True):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.isClosed = False

    def onInit(self):
        self.wifilist = self.getControl(WIFI_LIST_CONTROL)
        self.wifihelper = WiFiHelper(self.wifilist, __language__)
        self.wifihelper.FillList()
        self.setFocus(self.wifilist)        

        #li = xbmcgui.ListItem(__language__(33014),self.audioHelper.getSelectedOutput(),"")
        #self.audioSourceListControl.addItem(li)

    def isComplete(self): 
        return self.isClosed 

    def onAction(self, action):
        #print "Action Id -> {0}".format(action.getId())
        if (action.getId() == ACTION_PREVIOUS_MENU or action.getId() == ACTION_NAV_BACK ):
            self.close()
        elif (action.getId() == ACTION_SELECT_ITEM or action.getId() == ACTION_MOUSE_LEFT_CLICK):
            #print "Focused Item is {0}".format(self.getFocusId())
            pass

    def onClick(self, controlID):
        #print "onClick {0}".format(controlID)
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """

        if controlID == WIFI_LIST_CONTROL:
            item = self.wifilist.getSelectedItem()
            self.wifihelper.TakeAction(item) 
            self.setFocus(self.wifilist)         


    def close(self):
        self.isClosed = True 
        xbmcgui.WindowXML.close(self)    

networkSettingWindow = NetworkSettingsWindow("awnetworksettings.xml",__addon__.getAddonInfo('path'), "Default")
networkSettingWindow.show()
monitor = xbmc.Monitor()
while not networkSettingWindow.isComplete(): 
    if monitor.waitForAbort(2):
        # Abort was requested while waiting. We should exit
        break
    if (xbmcgui.getCurrentWindowId() == 10000):
        break

del networkSettingWindow
