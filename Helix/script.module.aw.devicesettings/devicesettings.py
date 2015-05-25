import xbmc
import xbmcgui
import xbmcaddon
import thread
import sys
from resources.lib.dialogselect import SelectDialog
from resources.lib.dialogupdateselect import UpdateSelectDialog

from resources.lib.audiohelper import AudioHelper
from resources.lib.spincontrol import SpinControl
from resources.lib.alienfxlights import AlienFXLights
from resources.lib.wirelessnetwork import WiFiHelper
from resources.lib.bluetooth import BluetoothHelper

AUDIO_SOURCE_LABLE_CONTROL = 106
AUDIO_SOURCE_ACTION_CONTROL = 107
AUDIO_SPEAKER_CONFIG_LABLE_CONTROL = 108
AUDIO_SPEAKER_CONFIG_ACTION_CONTROL = 109
AUDIO_VOLUME_LABLE_CONTROL = 110
AUDIO_VOLUME_SLIDER_CONTROL = 111
AUDIO_VOLUME_MINUS_BUTTON_CONTROL = 112
AUDIO_VOLUME_PLUS_BUTTON_CONTROL = 113
AUDIO_VOLUME_MUTE_RADIO_CONTROL = 114

ALIENFX_HEAD_GROUP_CONTROL = 116
ALIENFX_HEAD_SPIN_LEFT = 117
ALIENFX_HEAD_LABEL_CONTROL = 118
ALIENFX_HEAD_SPIN_RIGHT = 119
ALIENFX_HEAD_LEFT_FOCUS = 120
ALIENFX_HEAD_RIGHT_FOCUS = 121

ALIENFX_CORNER_GROUP_CONTROL = 124
ALIENFX_CORNER_SPIN_LEFT = 125
ALIENFX_CORNER_LABEL_CONTROL = 126
ALIENFX_CORNER_SPIN_RIGHT = 127
ALIENFX_CORNER_LEFT_FOCUS = 128
ALIENFX_CORNER_RIGHT_FOCUS = 129

ALIENFX_BRIGHTNESS_GROUP_CONTROL = 134
ALIENFX_BRIGHTNESS_SPIN_LEFT = 135
ALIENFX_BRIGHTNESS_IMAGE_CONTROL = 136
ALIENFX_BRIGHTNESS_LABEL_CONTROL = 137
ALIENFX_BRIGHTNESS_SPIN_RIGHT = 138
ALIENFX_BRIGHTNESS_LEFT_FOCUS = 139
ALIENFX_BRIGHTNESS_RIGHT_FOCUS = 140

BLUETOOTH_ON_RADIO_BUTTON_CONTROL = 151
BLUETOOTH_DISCOVERABILITY_ON_RADIO_BUTTON_CONTROL = 152
BLUETOOTH_DEVICES_LIST_CONTROL = 154

WIFI_LIST_CONTROL = 146
WIFI_NETWORK_LABEL_CONTROL = 147

UPDATE_WINDOWS_LABEL_CONTROL = 161
UPDATE_WINDOWS_BUTTON_CONTROL = 162
UPDATE_NVIDIA_LABEL_CONTROL = 163
UPDATE_NVIDIA_BUTTON_CONTROL = 164
UPDATE_ALIENWARE_LABEL_CONTROL = 165
UPDATE_ALIENWARE_BUTTON_CONTROL = 166

ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

ACTION_MOUSE_LEFT_CLICK = 100
ACTION_MOUSE_DRAG = 106

__scriptID__   = 'script.module.aw.devicesettings'
__addon__ = xbmcaddon.Addon(id=__scriptID__)
__language__ = __addon__.getLocalizedString

class DeviceSettingsWindow(xbmcgui.WindowXML):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback=True):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.IsInitDone = False
        self.isClosed = False
        self.updateWindowSetting = None
        self.updateNvidiaSetting = None
        self.updateAlienwareSetting = None

    def onInit(self):
        self.audioSourceLabelControl = self.getControl(AUDIO_SOURCE_LABLE_CONTROL)
        self.audioSpeakerConfigLabelControl = self.getControl(AUDIO_SPEAKER_CONFIG_LABLE_CONTROL)
        self.audioHelper = AudioHelper()  

        self.audioSourceLabelControl.setLabel(self.audioHelper.getSelectedOutput())

        self.audioSourceSelectedIndex = self.audioHelper.getSelectedIndex()      

        self.updateSpeakerConfig(self.audioSourceSelectedIndex)

        self.audioVolumeLabelControl = self.getControl(AUDIO_VOLUME_LABLE_CONTROL)
        self.audioVolumeSliderControl = self.getControl(AUDIO_VOLUME_SLIDER_CONTROL)
        self.audioVolumeMinusButtonControl = self.getControl(AUDIO_VOLUME_MINUS_BUTTON_CONTROL)
        self.audioVolumePlusButtonControl = self.getControl(AUDIO_VOLUME_PLUS_BUTTON_CONTROL)
        self.audioVolumeMuteRadioControl = self.getControl(AUDIO_VOLUME_MUTE_RADIO_CONTROL)

        volume = self.audioHelper.getVolume()
        self.audioVolumeSliderControl.setPercent(volume)
        self.audioVolumeLabelControl.setLabel("{0}%".format(volume))
        self.setVolumeControlButtons(volume)

        self.wifilist = self.getControl(WIFI_LIST_CONTROL)
        self.wifiNetworkLabelControl = self.getControl(WIFI_NETWORK_LABEL_CONTROL)
        self.wifihelper = WiFiHelper(self.wifilist, __language__)
        self.wifihelper.FillList()

        self.spinControls = []
        self.alienFXControls = AlienFXLights(self)

        alienFxBrightness = []

        for x in range(0,101):
            alienFxBrightness.append('{0}%'.format(x))

        self.alienFxHeadSpinControl = SpinControl(self,ALIENFX_HEAD_GROUP_CONTROL,ALIENFX_HEAD_LABEL_CONTROL,self.alienFxHeadColorChanged, self.alienFxHeadUpCallback, self.alienFxHeadDownCallback, self.alienFXControls.colors,ALIENFX_HEAD_SPIN_LEFT, ALIENFX_HEAD_SPIN_RIGHT, ALIENFX_HEAD_LEFT_FOCUS, ALIENFX_HEAD_RIGHT_FOCUS)
        self.alienFxHeadSpinControl.selectText(self.alienFXControls.zone1SelectedColor)

        self.alienFxCornerSpinControl = SpinControl(self,ALIENFX_CORNER_GROUP_CONTROL,ALIENFX_CORNER_LABEL_CONTROL,self.alienFxCornerColorChanged, self.alienFxCornerUpCallback, self.alienFxCornerDownCallback, self.alienFXControls.colors,ALIENFX_CORNER_SPIN_LEFT, ALIENFX_CORNER_SPIN_RIGHT, ALIENFX_CORNER_LEFT_FOCUS, ALIENFX_CORNER_RIGHT_FOCUS)
        self.alienFxCornerSpinControl.selectText(self.alienFXControls.zone2SelectedColor)

        self.alienFxBrightnessImageControl = self.getControl(ALIENFX_BRIGHTNESS_IMAGE_CONTROL)
        self.alienFxBrightnessSpinControl = SpinControl(self,ALIENFX_BRIGHTNESS_GROUP_CONTROL,ALIENFX_BRIGHTNESS_LABEL_CONTROL,self.alienFxBrightnessChanged, self.alienFxBrightnessUpCallback, self.alienFxBrightnessDownCallback, alienFxBrightness,ALIENFX_BRIGHTNESS_SPIN_LEFT, ALIENFX_BRIGHTNESS_SPIN_RIGHT, ALIENFX_BRIGHTNESS_LEFT_FOCUS,ALIENFX_BRIGHTNESS_RIGHT_FOCUS)
        self.alienFxBrightnessSpinControl.selectText('{0}%'.format(self.alienFXControls.brightnessSpinIndex))
        self.setAlienFxBrightnessImage(self.alienFXControls.brightnessSpinIndex)
        
        self.spinControls.append(self.alienFxHeadSpinControl)  
        self.spinControls.append(self.alienFxCornerSpinControl)  
        self.spinControls.append(self.alienFxBrightnessSpinControl)  

        self.bluetoothOnRadioButton = self.getControl(BLUETOOTH_ON_RADIO_BUTTON_CONTROL)
        self.bluetoothDiscoverabilityRadioButton = self.getControl(BLUETOOTH_DISCOVERABILITY_ON_RADIO_BUTTON_CONTROL)
        self.bluetoothDevicesListControl = self.getControl(BLUETOOTH_DEVICES_LIST_CONTROL)

        self.bluetoothHelper = BluetoothHelper(self.bluetoothDevicesListControl,__addon__,__language__)
        self.bluetoothOnRadioButton.setSelected(self.bluetoothHelper.isBluetoothOn())

        self.updateWindowLabelControl = self.getControl(UPDATE_WINDOWS_LABEL_CONTROL)
        self.updateNvidiaLabelControl = self.getControl(UPDATE_NVIDIA_LABEL_CONTROL)
        self.updateAlienwareLabelControl = self.getControl(UPDATE_ALIENWARE_LABEL_CONTROL)

        self.refreshMute()

        self.lock = thread.allocate_lock()

        self.IsInitDone = True

    def isComplete(self): 
        return self.isClosed 

    def onAction(self, action):
        if action.getId() != ACTION_SELECT_ITEM:
            for control in self.spinControls:
                retVal = control.forwardInput(action.getId(), 0)
                if retVal:
                    #print "returning true"
                    return;

        if (action.getId() == ACTION_PREVIOUS_MENU or action.getId() == ACTION_NAV_BACK ):
            self.lock.acquire()
            self.IsInitDone = False
            self.lock.release()
            self.alienFXControls.release()
            self.close()
        elif (action.getId() == ACTION_MOVE_DOWN):
            #print "move down -> {0}".format(self.getFocusId())
            #if(self.getFocusId() == BLUETOOTH_ON_RADIO_BUTTON_CONTROL):
            #    if(self.bluetoothOnRadioButton.isSelected()):
            #        self.setFocusId(BLUETOOTH_DISCOVERABILITY_ON_RADIO_BUTTON_CONTROL)
            #    else:
            #        self.setFocusId(BLUETOOTH_DEVICES_LIST_CONTROL)
            #        self.bluetoothDevicesListControl.selectItem(0)
            #elif(self.getFocusId() == BLUETOOTH_DISCOVERABILITY_ON_RADIO_BUTTON_CONTROL):
            #    self.setFocusId(BLUETOOTH_DEVICES_LIST_CONTROL)
            #    self.bluetoothDevicesListControl.selectItem(0)
            #elif (self.getFocusId() == BLUETOOTH_DEVICES_LIST_CONTROL and self.bluetoothDevicesListControl.getSelectedPosition() == 0):
            #    self.setFocusId(BLUETOOTH_ON_RADIO_BUTTON_CONTROL)
            pass
        elif (action.getId() == ACTION_MOVE_UP):
            #print "move down -> {0}".format(self.getFocusId())
            #if(self.getFocusId() == BLUETOOTH_ON_RADIO_BUTTON_CONTROL):
            #    self.setFocusId(BLUETOOTH_DEVICES_LIST_CONTROL)
            #    self.bluetoothDevicesListControl.selectItem(self.bluetoothDevicesListControl.size() - 1)
            #elif(self.getFocusId() == BLUETOOTH_DISCOVERABILITY_ON_RADIO_BUTTON_CONTROL):
            #    self.setFocusId(BLUETOOTH_ON_RADIO_BUTTON_CONTROL)
            #elif (self.getFocusId() == BLUETOOTH_DEVICES_LIST_CONTROL and self.bluetoothDevicesListControl.getSelectedPosition() == (self.bluetoothDevicesListControl.size() - 1)):
            #    if(self.bluetoothOnRadioButton.isSelected()):
            #        self.setFocusId(BLUETOOTH_DISCOVERABILITY_ON_RADIO_BUTTON_CONTROL)
            #    else:
            #       self.setFocusId(BLUETOOTH_ON_RADIO_BUTTON_CONTROL)
            pass
        elif (action.getId() == ACTION_SELECT_ITEM or action.getId() == ACTION_MOUSE_LEFT_CLICK):
            #print "Focused Item is {0}".format(self.getFocusId())
            if (self.getFocusId() == AUDIO_SOURCE_ACTION_CONTROL):
                dialog = SelectDialog("awdialogselect.xml",__addon__.getAddonInfo('path'), "Default")
                dialog._title = __language__(33015)
                dialog._optionList = self.audioHelper.getOutputs()
                dialog.doModal()
                if (dialog._selectedOptionPosition is not None):
                    if (self.audioHelper.setOutput(dialog._selectedOptionPosition)):
                        self.audioSourceSelectedIndex = dialog._selectedOptionPosition
                        self.audioSourceLabelControl.setLabel(self.audioHelper.getOutputNameFromIndex(self.audioSourceSelectedIndex))
                        self.updateSpeakerConfig(self.audioSourceSelectedIndex)
                        self.refreshMute()
                        xbmcgui.Dialog().notification(__language__(33020), __language__(33021), xbmcgui.NOTIFICATION_INFO, 15000)
                    else:
                        xbmcgui.Dialog().notification(__language__(33018), __language__(33019), xbmcgui.NOTIFICATION_ERROR, 15000)
                del dialog 
            elif (self.getFocusId() == AUDIO_SPEAKER_CONFIG_ACTION_CONTROL):
                dialog = SelectDialog("awdialogselect.xml",__addon__.getAddonInfo('path'), "Default")
                dialog._title = __language__(33039)
                dialog._optionList = self.audioHelper.getSpeakerConfigs(self.audioSourceSelectedIndex)
                dialog.doModal()
                if (dialog._selectedOptionPosition is not None):
                    if (self.audioHelper.setSpeakerConfig(self.audioSourceSelectedIndex,dialog._selectedOptionPosition)):
                        self.updateSpeakerConfig(self.audioSourceSelectedIndex)
                        self.refreshMute()
                        xbmcgui.Dialog().notification(__language__(33020), __language__(33045), xbmcgui.NOTIFICATION_INFO, 15000)
                    else:
                        xbmcgui.Dialog().notification(__language__(33018), __language__(33046), xbmcgui.NOTIFICATION_ERROR, 15000)
                del dialog 
            elif(self.getFocusId() == AUDIO_VOLUME_MUTE_RADIO_CONTROL):
                self.audioHelper.setMute(self.audioVolumeMuteRadioControl.isSelected())
            elif (self.getFocusId() == BLUETOOTH_DEVICES_LIST_CONTROL):
                self.bluetoothHelper.authenticateOrRemoveDevice(self.bluetoothDevicesListControl.getSelectedItem().getProperty('Address'))
            elif (self.getFocusId() == UPDATE_WINDOWS_BUTTON_CONTROL):
                updateDialog = UpdateSelectDialog("awdialogupdateselect.xml",__addon__.getAddonInfo('path'), "Default", selectedUpdateOption = self.updateWindowSetting)
                updateDialog._title = __language__(33065)
                updateDialog.doModal()
                if (updateDialog.getSelectedRadionButton() is not None):
                    self.updateWindowSetting = updateDialog.getSelectedRadionButton()
                    self.updateWindowLabelControl.setLabel(__language__(33069 + self.updateWindowSetting))
                del updateDialog 

            elif (self.getFocusId() == UPDATE_NVIDIA_BUTTON_CONTROL):
                updateDialog = UpdateSelectDialog("awdialogupdateselect.xml",__addon__.getAddonInfo('path'), "Default", selectedUpdateOption = self.updateNvidiaSetting)
                updateDialog._title = __language__(33065)
                updateDialog.doModal()
                if (updateDialog.getSelectedRadionButton() is not None):
                    self.updateNvidiaSetting = updateDialog.getSelectedRadionButton()
                    self.updateNvidiaLabelControl.setLabel(__language__(33069 + self.updateNvidiaSetting))
                del updateDialog 

            elif (self.getFocusId() == UPDATE_ALIENWARE_BUTTON_CONTROL):
                updateDialog = UpdateSelectDialog("awdialogupdateselect.xml",__addon__.getAddonInfo('path'), "Default", selectedUpdateOption = self.updateAlienwareSetting)
                updateDialog._title = __language__(33065)
                updateDialog.doModal()
                if (updateDialog.getSelectedRadionButton() is not None):
                    self.updateAlienwareSetting = updateDialog.getSelectedRadionButton()
                    self.updateAlienwareLabelControl.setLabel(__language__(33069 + self.updateAlienwareSetting))
                del updateDialog 

    def onClick(self, controlID):
        #print "onClick {0}".format(controlID)
        for control in self.spinControls:
            retVal = control.forwardInput(ACTION_SELECT_ITEM, controlID)
            if retVal:
                return;
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
        if (self.getFocusId() == AUDIO_VOLUME_MINUS_BUTTON_CONTROL or self.getFocusId() == AUDIO_VOLUME_PLUS_BUTTON_CONTROL):            
            volume = int(self.audioVolumeSliderControl.getPercent())
            if (self.getFocusId() == AUDIO_VOLUME_MINUS_BUTTON_CONTROL):
                if (volume > 0):
                    volume -= 1
            elif (self.getFocusId() == AUDIO_VOLUME_PLUS_BUTTON_CONTROL):            
                if (volume < 100):
                    volume += 1
            self.audioHelper.setVolume(volume)
            self.audioVolumeSliderControl.setPercent(volume)                
            self.audioVolumeLabelControl.setLabel("{0}%".format(volume))
            self.setVolumeControlButtons(volume)
            self.refreshMute()

        elif controlID == WIFI_LIST_CONTROL:
            item = self.wifilist.getSelectedItem()
            self.wifihelper.TakeAction(item) 
            self.setFocus(self.wifilist)         
    
    def setVolumeControlButtons(self, volume):
            self.audioVolumeMinusButtonControl.setEnabled(True)
            self.audioVolumePlusButtonControl.setEnabled(True)
            if (volume == 0):
                self.audioVolumeMinusButtonControl.setEnabled(False)
                self.setFocus(self.audioVolumePlusButtonControl)
            elif (volume == 100):
                self.audioVolumePlusButtonControl.setEnabled(False)
                self.setFocus(self.audioVolumeMinusButtonControl)

    def close(self):
        self.bluetoothHelper.close()
        self.isClosed = True 
        xbmcgui.WindowXML.close(self)    

    def updateSpeakerConfig(self, selectedIndex):
        selectedSpeakerConfig = self.audioHelper.getSelectedSpeakerConfig(selectedIndex)

        if (selectedSpeakerConfig is None):
            self.audioSpeakerConfigLabelControl.setEnabled(False)
            self.audioSpeakerConfigLabelControl.setLabel(__language__(33038))
        else:
            self.audioSpeakerConfigLabelControl.setEnabled(True)
            self.audioSpeakerConfigLabelControl.setLabel(selectedSpeakerConfig)

    def setAlienFxBrightnessImage(self, brightness):
        #print "setAlienFxBrightnessImage {0}".format(brightness)
        self.alienFxBrightnessImageControl.setVisible(brightness != 0)    

        self.alienFxBrightnessImageControl.setWidth(260 * brightness/100)
        #print "image size {0} ".format(205 * brightness/100)

    def refreshMute(self):
        self.audioVolumeMuteRadioControl.setSelected(self.audioHelper.isMute())

    ############################################################################################
    ################################# ALIENFX Callbacks ########################################

    def alienFxHeadColorChanged(self,selectedIndex,selectedText,previousSelectedIndex,previousSelectedText):
        if self.IsInitDone:
            #print "alienFxHeadColorChanged {0}".format(selectedIndex)
            self.alienFXControls.setColor(1,selectedIndex)
            pass

    def alienFxHeadUpCallback(self, fromControl):
        #print "alienFxHeadUpCallback"
        self.alienFxBrightnessSpinControl.setFocus(fromControl == self.alienFxHeadSpinControl.leftArrow)
        pass 

    def alienFxHeadDownCallback(self, fromControl):
        #print "alienFxHeadDownCallback"
        self.alienFxCornerSpinControl.setFocus(fromControl == self.alienFxHeadSpinControl.leftArrow)
        pass 

    def alienFxCornerColorChanged(self,selectedIndex,selectedText,previousSelectedIndex,previousSelectedText):
        if self.IsInitDone:
            self.alienFXControls.setColor(2,selectedIndex)
            pass

    def alienFxCornerUpCallback(self, fromControl):
        #print "alienFxCornerUpCallback"
        self.alienFxHeadSpinControl.setFocus(fromControl == self.alienFxCornerSpinControl.leftArrow)
        pass 

    def alienFxCornerDownCallback(self, fromControl):
        #print "alienFxCornerDownCallback"
        self.alienFxBrightnessSpinControl.setFocus(fromControl == self.alienFxCornerSpinControl.leftArrow)
        pass 

    def alienFxBrightnessChanged(self,selectedIndex,selectedText,previousSelectedIndex,previousSelectedText):
        if self.IsInitDone:            
            self.setAlienFxBrightnessImage(selectedIndex)
            self.alienFXControls.setBrightness(selectedIndex)
            pass

    def alienFxBrightnessUpCallback(self, fromControl):
        #print "alienFxCornerUpCallback"
        self.alienFxCornerSpinControl.setFocus(fromControl == self.alienFxBrightnessSpinControl.leftArrow)
        pass 

    def alienFxBrightnessDownCallback(self, fromControl):
        #print "alienFxCornerDownCallback"
        self.alienFxHeadSpinControl.setFocus(fromControl == self.alienFxBrightnessSpinControl.leftArrow)
        pass 

    #############################################################################################


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
