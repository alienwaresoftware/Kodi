import xbmc
import xbmcgui
import os

ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

class ScaleToScreenXML(xbmcgui.WindowXMLDialog):
    def onAction(self, action):
        #print "ACtion %s" % action.getId()
        if action == ACTION_SELECT_ITEM:
            self.close()

    def onClick(self, controlID):
        self.close()

mywin = ScaleToScreenXML("scaletoscreen.xml",os.getcwd())
mywin.doModal()
del mywin
