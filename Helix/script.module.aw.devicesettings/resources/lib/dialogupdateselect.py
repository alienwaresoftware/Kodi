import xbmc
import xbmcgui
import xbmcaddon
import sys

ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
ACTION_MOUSE_LEFT_CLICK = 100

DIALOG_TITLE_LABEL_CONTROL = 101
UPDATE_NOW_BUTTON_CONTROL = 103
AUTOMATIC_UPDATE_RADIO_BUTTON_CONTROL = 105
CLOSE_AT_UPDATE_RADIO_BUTTON_CONTROL = 106
MANUAL_UPDATE_RADIO_BUTTON_CONTROL = 107

__scriptID__   = 'script.module.aw.devicesettings'
__addon__ = xbmcaddon.Addon(id=__scriptID__)

class UpdateSelectDialog(xbmcgui.WindowXMLDialog):
    _title = None
    _selectedUdpateOption = None

    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback=True, selectedUpdateOption=None, isAutomaticUpdateVisible=True, isCloseAtUpdateVisible=True, isManualUpdateVisible = True):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self._isAutomaticUpdateVisible = isAutomaticUpdateVisible
        self._isCloseAtUpdateVisible = isCloseAtUpdateVisible
        self._isManualUpdateVisible = isManualUpdateVisible
        self._selectedUdpateOption = selectedUpdateOption
        pass

    def onInit(self):
        self.getControl(DIALOG_TITLE_LABEL_CONTROL).setLabel(self._title)
        self.udpateNowButtonControl = self.getControl(UPDATE_NOW_BUTTON_CONTROL)

        self.radioButtons = []

        self.automaticUpdateRadioButtonControl = self.getControl(AUTOMATIC_UPDATE_RADIO_BUTTON_CONTROL)
        self.automaticUpdateRadioButtonControl.setVisible(self._isAutomaticUpdateVisible)
        if (self._isAutomaticUpdateVisible):
            self.radioButtons.append(self.automaticUpdateRadioButtonControl)

        self.closeAtUpdateRadioButtonControl = self.getControl(CLOSE_AT_UPDATE_RADIO_BUTTON_CONTROL)
        self.closeAtUpdateRadioButtonControl.setVisible(self._isCloseAtUpdateVisible)
        if (self._isCloseAtUpdateVisible):
            self.radioButtons.append(self.closeAtUpdateRadioButtonControl)

        self.manuaUpdateRadioButtonControl = self.getControl(MANUAL_UPDATE_RADIO_BUTTON_CONTROL)
        self.manuaUpdateRadioButtonControl.setVisible(self._isManualUpdateVisible)
        if (self._isManualUpdateVisible):
            self.radioButtons.append(self.manuaUpdateRadioButtonControl)
        
        if (self._selectedUdpateOption == 1):
            self.automaticUpdateRadioButtonControl.setSelected(True)
        elif (self._selectedUdpateOption == 2):
            self.closeAtUpdateRadioButtonControl.setSelected(True)
        elif (self._selectedUdpateOption == 3):
            self.manuaUpdateRadioButtonControl.setSelected(True)

        self.setFocus(self.udpateNowButtonControl) 

    def deselectRadioButtons(self):
        for radioButton in self.radioButtons:
            radioButton.setSelected(False)     
            
    def getSelectedRadionButton(self):
        return self._selectedUdpateOption     

    def onAction(self, action):
        if (action.getId() == ACTION_PREVIOUS_MENU or action.getId() == ACTION_NAV_BACK ):
            self.close()
        elif (action.getId() == ACTION_SELECT_ITEM or action.getId() == ACTION_MOUSE_LEFT_CLICK ):
            if (self.getFocusId() == AUTOMATIC_UPDATE_RADIO_BUTTON_CONTROL):
                self.deselectRadioButtons()
                self.automaticUpdateRadioButtonControl.setSelected(True)
                self._selectedUdpateOption = 1
            elif (self.getFocusId() == CLOSE_AT_UPDATE_RADIO_BUTTON_CONTROL):
                self.deselectRadioButtons()
                self.closeAtUpdateRadioButtonControl.setSelected(True)
                self._selectedUdpateOption = 2
            elif (self.getFocusId() == MANUAL_UPDATE_RADIO_BUTTON_CONTROL):
                self.deselectRadioButtons()
                self.manuaUpdateRadioButtonControl.setSelected(True)
                self._selectedUdpateOption = 3
            self.close()
