import xbmc
import xbmcgui
import xbmcaddon
import sys

ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
ACTION_MOUSE_LEFT_CLICK = 100

DIALOG_TITLE_LABEL_CONTROL = 101
OPTION_LIST_CONTROL = 102

__scriptID__   = 'script.module.aw.devicesettings'
__addon__ = xbmcaddon.Addon(id=__scriptID__)

class SelectDialog(xbmcgui.WindowXMLDialog):
    _title = None
    _optionList = None
    _selectedOptionPosition = None

    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback=True):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        pass

    def onInit(self):
        self._selectedOptionPosition = None
        self.getControl(DIALOG_TITLE_LABEL_CONTROL).setLabel(self._title)
        self.optionListControl = self.getControl(OPTION_LIST_CONTROL)

        for option in self._optionList :
            li = xbmcgui.ListItem(option,"","")
            self.optionListControl.addItem(li)

        self.setFocus(self.optionListControl)           

    def onAction(self, action):
        if (action.getId() == ACTION_PREVIOUS_MENU or action.getId() == ACTION_NAV_BACK ):
            self.close()
        elif (action.getId() == ACTION_SELECT_ITEM or action.getId() == ACTION_MOUSE_LEFT_CLICK ):
            self._selectedOptionPosition = self.optionListControl.getSelectedPosition()
            self.close()
