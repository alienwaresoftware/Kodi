import xbmc
import xbmcgui
import xbmcaddon
import sys

ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
ACTION_MOUSE_LEFT_CLICK = 100

DIALOG_TITLE_LABEL_CONTROL = 101

__scriptID__   = 'script.module.aw.devicesettings'
__addon__ = xbmcaddon.Addon(id=__scriptID__)
__language__ = __addon__.getLocalizedString

class WaitDialog(xbmcgui.WindowXMLDialog):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback=True):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.isInitDone = False
        pass

    def onInit(self):
        self.titleLabelControl = self.getControl(DIALOG_TITLE_LABEL_CONTROL)
        self.isInitDone = True

    def setLabel(self, text):
        self.titleLabelControl.setLabel(text)

class WaitDialogHelper():
    def __init__(self):
        pass
        
    def create(self):
        waitDialog = WaitDialog("awwaitdialog.xml",__addon__.getAddonInfo('path'), "Default")
        waitDialog.show()
        while(not waitDialog.isInitDone):
            xbmc.sleep(5)
        return waitDialog

