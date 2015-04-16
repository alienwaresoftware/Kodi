import xbmc
import xbmcgui
import os

ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_LEFT = 1

class HelpXML(xbmcgui.WindowXMLDialog):
    def onInit(self):
        self.depth = 0 

    def onAction(self, action):
        if action == ACTION_MOVE_RIGHT and self.depth == 0:
            self.depth = 1
            self.setFocusId(9011)
        if (action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK):
            self.close()
        if action == ACTION_MOVE_LEFT and self.depth == 1:
            self.depth = 0
            self.setFocusId(9000)

mywin = HelpXML("Help.xml",os.getcwd())
mywin.doModal()
del mywin
