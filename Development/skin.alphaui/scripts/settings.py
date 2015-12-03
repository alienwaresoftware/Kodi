import xbmc
import xbmcgui
import os
import thread
from wirelessnetwork import WiFiHelper
from spincontrol import SpinControl
from hdmiinhelper import HDMIInHelper
from displayhelper import DisplayHelper
from audiohelper import AudioHelper
from addon import AlienFXLights
from confirmdialog import ConfirmDialog
from confirmdialog import ConfirmDialogType
from threading import Timer
import AlphaUIUtils

SPIN_ARROW_LEFT_TEXURE_NORMAL = "special://skin/media/alienware/spinarrow.png"
SPIN_ARROW_LEFT_TEXURE_DISABLE = "special://skin/media/alienware/spinarrowdisable.png"

VIDEO_LIST_CONTROL = 9011
DISPLAY_RESOLUTION_GROUP_CONTROL = 9013
DISPLAY_RESOLUTION_SPIN_LEFT = 9014
DISPLAY_RESOLUTION_LABEL_CONTROL = 9015
DISPLAY_RESOLUTION_SPIN_RIGHT = 9016
DISPLAY_RESOLUTION_LEFT_FOCUS = 9025
DISPLAY_RESOLUTION_RIGHT_FOCUS = 9026

REFRESH_RATE_GROUP_CONTROL = 9018
REFRESH_RATE_SPIN_LEFT = 9019
REFRESH_RATE_LABEL_CONTROL = 9020
REFRESH_RATE_SPIN_RIGHT = 9021
REFRESH_RATE_LEFT_FOCUS = 9027
REFRESH_RATE_RIGHT_FOCUS = 9028

VIDEO_APPLY_BUTTON_CONTROL = 9023

AUDIO_OUTPUT_GROUP_CONTROL = 9033
AUDIO_OUTPUT_SPIN_LEFT = 9034
AUDIO_OUTPUT_LABEL_CONTROL = 9035
AUDIO_OUTPUT_SPIN_RIGHT = 9036
AUDIO_OUTPUT_LEFT_FOCUS = 9037
AUDIO_OUTPUT_RIGHT_FOCUS = 9038

AUDIO_OUTPUT_APPLY_BUTTON = 9039

AUDIO_VOLUME_GROUP_CONTROL = 9041
AUDIO_VOLUME_SPIN_LEFT = 9042
AUDIO_VOLUME_IMAGE_CONTROL = 9043
AUDIO_VOLUME_LABEL_CONTROL = 9044
AUDIO_VOLUME_SPIN_RIGHT = 9045
AUDIO_VOLUME_LEFT_FOCUS = 9046
AUDIO_VOLUME_RIGHT_FOCUS = 9047

ALIENFX_GROUP_CONTROL = 9080
ALIENFX_LIST_CONTROL = 9081
ALIENFX_DUMMY_CONTROL = 9082

ALIENFX_HEAD_GROUP_CONTROL = 9083
ALIENFX_HEAD_SPIN_LEFT = 9084
ALIENFX_HEAD_LABEL_CONTROL = 9085
ALIENFX_HEAD_SPIN_RIGHT = 9086
ALIENFX_HEAD_LEFT_FOCUS = 9087
ALIENFX_HEAD_RIGHT_FOCUS = 9088

ALIENFX_CORNER_GROUP_CONTROL = 9091
ALIENFX_CORNER_SPIN_LEFT = 9092
ALIENFX_CORNER_LABEL_CONTROL = 9093
ALIENFX_CORNER_SPIN_RIGHT = 9094
ALIENFX_CORNER_LEFT_FOCUS = 9095
ALIENFX_CORNER_RIGHT_FOCUS = 9096

ALIENFX_BRIGHTNESS_GROUP_CONTROL = 9101
ALIENFX_BRIGHTNESS_SPIN_LEFT = 9102
ALIENFX_BRIGHTNESS_IMAGE_CONTROL = 9103
ALIENFX_BRIGHTNESS_LABEL_CONTROL = 9104
ALIENFX_BRIGHTNESS_SPIN_RIGHT = 9105
ALIENFX_BRIGHTNESS_LEFT_FOCUS = 9106
ALIENFX_BRIGHTNESS_RIGHT_FOCUS = 9107

NETWORK_LIST_CONTROL = 9051
WIFI_LIST_ITEM = 9052
ETHERNET_LIST_ITEM = 9053
WIFI_LIST_CONTROL = 9055
HDMIIN_LIST_CONTROL = 9071
HDMIIN_BUTTON_CONTROL = 9075

ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

class SettingsXML(xbmcgui.WindowXMLDialog):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName="test", forceFallback="True"):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        
        self.IsInitDone = False
        self.IsInResolutionChange = False

        pass

    def onInit(self):

        # Put your List Populating code/ and GUI startup stuff here
        self.spinControls = []

        self.displayHelper = DisplayHelper()
        self.audioHelper = AudioHelper()
        self.alienFXControls = AlienFXLights(self)
        self.hdmiinhelper = HDMIInHelper()

        # Video Controls
        self.displayResolutionApplyButtonState = True
        self.displayResolutions = self.displayHelper.getAllDisplayResolutions()
        self.displayResolutionSpinControl = SpinControl(self,DISPLAY_RESOLUTION_GROUP_CONTROL,DISPLAY_RESOLUTION_LABEL_CONTROL,self.displayResolutionChanged, self.displayResolutionUpCallback, self.displayResolutionDownCallback, self.displayResolutions,DISPLAY_RESOLUTION_SPIN_LEFT, DISPLAY_RESOLUTION_SPIN_RIGHT, DISPLAY_RESOLUTION_LEFT_FOCUS, DISPLAY_RESOLUTION_RIGHT_FOCUS)
        self.displayResolutionSpinControl.selectText(self.displayHelper.getSelectedDisplayResolution())
        self.displayResolutionApplyButton = self.getControl(VIDEO_APPLY_BUTTON_CONTROL);
                
        self.refreshRates = self.displayHelper.getAllRefreshRates()
        self.refreshRateSpinControl = SpinControl(self,REFRESH_RATE_GROUP_CONTROL,REFRESH_RATE_LABEL_CONTROL, self.refreshRateChanged, self.refreshRateUpCallback, self.refreshRateDownCallback,self.refreshRates, REFRESH_RATE_SPIN_LEFT, REFRESH_RATE_SPIN_RIGHT, REFRESH_RATE_LEFT_FOCUS, REFRESH_RATE_RIGHT_FOCUS)
        self.refreshRateSpinControl.selectText(self.displayHelper.getSelectedRefreshRate())

        self.setDisplayApplyButtonState()
               
         
        # Audio Controls        
        self.audioOutputApplyButtonState = True

        self.audioOutputSpinControl = SpinControl(self,AUDIO_OUTPUT_GROUP_CONTROL,AUDIO_OUTPUT_LABEL_CONTROL, self.audioOutputChanged, self.audioOutputUpCallback, self.audioOutputDownCallback,self.audioHelper.getOutputs(), AUDIO_OUTPUT_SPIN_LEFT, AUDIO_OUTPUT_SPIN_RIGHT, AUDIO_OUTPUT_LEFT_FOCUS, AUDIO_OUTPUT_RIGHT_FOCUS)
        self.audioOutputSpinControl.selectText(self.audioHelper.getSelectedOutput())
        self.audioOutputApplyButton = self.getControl(AUDIO_OUTPUT_APPLY_BUTTON);

        self.audioVolumeImageControl = self.getControl(AUDIO_VOLUME_IMAGE_CONTROL)

        self.setAudioOutputApplyButtonState()

        audioOptions = []
        alienFxBrightness = []

        for x in range(0,101):
            audioOptions.append('{0}%'.format(x))
            alienFxBrightness.append('{0}%'.format(x))
                        
        self.audioVolumeSpinControl = SpinControl(self,AUDIO_VOLUME_GROUP_CONTROL,AUDIO_VOLUME_LABEL_CONTROL,self.audioVolumeChanged, None, None, audioOptions,AUDIO_VOLUME_SPIN_LEFT, AUDIO_VOLUME_SPIN_RIGHT, AUDIO_VOLUME_LEFT_FOCUS,AUDIO_VOLUME_RIGHT_FOCUS)
        audioLevel = self.audioHelper.getVolume()
        self.audioVolumeSpinControl.selectText('{0}%'.format(audioLevel))
        self.setAudioVolumeImage(audioLevel)
        
        # Customization Controls

        self.alienFxHeadSpinControl = SpinControl(self,ALIENFX_HEAD_GROUP_CONTROL,ALIENFX_HEAD_LABEL_CONTROL,self.alienFxHeadColorChanged, self.alienFxHeadUpCallback, self.alienFxHeadDownCallback, self.alienFXControls.colors,ALIENFX_HEAD_SPIN_LEFT, ALIENFX_HEAD_SPIN_RIGHT, ALIENFX_HEAD_LEFT_FOCUS, ALIENFX_HEAD_RIGHT_FOCUS)
        self.alienFxHeadSpinControl.selectText(self.alienFXControls.zone1SelectedColor)

        self.alienFxCornerSpinControl = SpinControl(self,ALIENFX_CORNER_GROUP_CONTROL,ALIENFX_CORNER_LABEL_CONTROL,self.alienFxCornerColorChanged, self.alienFxCornerUpCallback, self.alienFxCornerDownCallback, self.alienFXControls.colors,ALIENFX_CORNER_SPIN_LEFT, ALIENFX_CORNER_SPIN_RIGHT, ALIENFX_CORNER_LEFT_FOCUS, ALIENFX_CORNER_RIGHT_FOCUS)
        self.alienFxCornerSpinControl.selectText(self.alienFXControls.zone2SelectedColor)

        self.alienFxBrightnessImageControl = self.getControl(ALIENFX_BRIGHTNESS_IMAGE_CONTROL)
        self.alienFxBrightnessSpinControl = SpinControl(self,ALIENFX_BRIGHTNESS_GROUP_CONTROL,ALIENFX_BRIGHTNESS_LABEL_CONTROL,self.alienFxBrightnessChanged, self.alienFxBrightnessUpCallback, self.alienFxBrightnessDownCallback, alienFxBrightness,ALIENFX_BRIGHTNESS_SPIN_LEFT, ALIENFX_BRIGHTNESS_SPIN_RIGHT, ALIENFX_BRIGHTNESS_LEFT_FOCUS,ALIENFX_BRIGHTNESS_RIGHT_FOCUS)
        self.alienFxBrightnessSpinControl.selectText('{0}%'.format(self.alienFXControls.brightnessSpinIndex))
        self.setAlienFxBrightnessImage(self.alienFXControls.brightnessSpinIndex)

        self.networklistcontrol = self.getControl(NETWORK_LIST_CONTROL)
        self.wifilist = self.getControl(WIFI_LIST_CONTROL)
        self.wifihelper = WiFiHelper(self.wifilist)

        self.hdmiinbutton = self.getControl(HDMIIN_BUTTON_CONTROL)      
        
        self.spinControls.append(self.displayResolutionSpinControl)  
        self.spinControls.append(self.refreshRateSpinControl)  
        self.spinControls.append(self.audioOutputSpinControl)          
        self.spinControls.append(self.audioVolumeSpinControl)  
        self.spinControls.append(self.alienFxHeadSpinControl)  
        self.spinControls.append(self.alienFxCornerSpinControl)  
        self.spinControls.append(self.alienFxBrightnessSpinControl)  

        self.lock = thread.allocate_lock()

        self.IsInitDone = True

        # start all timer now
        self.hdmistatechecktimer = Timer(1.0, self.refreshTimer)
        self.hdmistatechecktimer.start()

        pass
    
    def displayResolutionUpCallback(self, fromControl):
        #print "displayResolutionUpCallback"
        if self.displayResolutionApplyButtonState:
            self.setFocus(self.displayResolutionApplyButton);
        elif self.refreshRateSpinControl.rightArrowEnabled or self.refreshRateSpinControl.leftArrowEnabled:
            self.refreshRateSpinControl.setFocus(fromControl == self.displayResolutionSpinControl.leftArrow);
        pass 

    def displayResolutionDownCallback(self, fromControl):
        #print "displayResolutionDownCallback"
        if self.refreshRateSpinControl.rightArrowEnabled or self.refreshRateSpinControl.leftArrowEnabled:
            self.refreshRateSpinControl.setFocus(fromControl == self.displayResolutionSpinControl.leftArrow);
        elif self.displayResolutionApplyButtonState:
            self.setFocus(self.displayResolutionApplyButton);
        pass

    def setDisplayResolution(self):
        if self.IsInitDone and not self.IsInResolutionChange:                        
            self.IsInResolutionChange = True
            if not self.displayHelper.setMode(self.displayResolutionSpinControl.getSelectedIndex(),self.refreshRateSpinControl.getSelectedIndex()):
                self.displayResolutions = self.displayHelper.getAllDisplayResolutions()
                self.displayResolutionSpinControl.selectText(self.displayHelper.getSelectedDisplayResolution())
                self.refreshRates = self.displayHelper.getAllRefreshRates()
                self.refreshRateSpinControl.updateItems(self.refreshRates)
                self.refreshRateSpinControl.selectText(self.displayHelper.getSelectedRefreshRate())
            print self.getFocusId()
            self.getControl(VIDEO_LIST_CONTROL).selectItem(0)
            self.displayResolutionSpinControl.setFocus(True)
            self.setDisplayApplyButtonState()
            self.IsInResolutionChange = False

    def displayResolutionChanged(self,selectedIndex,selectedText,previousSelectedIndex,previousSelectedText):
        if self.IsInitDone and not self.IsInResolutionChange:
            self.IsInResolutionChange = True
            self.refreshRates = self.displayHelper.getRefreshRates(selectedIndex)
            self.refreshRateSpinControl.updateItems(self.refreshRates)
            self.setDisplayApplyButtonState()
            self.IsInResolutionChange = False
    
    def refreshRateUpCallback(self, fromControl):
        #print "refreshRateUpCallback"
        if self.displayResolutionSpinControl.rightArrowEnabled or self.displayResolutionSpinControl.leftArrowEnabled:
            self.displayResolutionSpinControl.setFocus(fromControl == self.refreshRateSpinControl.leftArrow);
        elif self.displayResolutionApplyButtonState:
            self.setFocus(self.displayResolutionApplyButton);
        pass 

    def refreshRateDownCallback(self, fromControl):
        #print "refreshRateDownCallback"
        if self.displayResolutionApplyButtonState:
            self.setFocus(self.displayResolutionApplyButton);
        elif self.displayResolutionSpinControl.rightArrowEnabled or self.displayResolutionSpinControl.leftArrowEnabled:
            self.displayResolutionSpinControl.setFocus(fromControl == self.refreshRateSpinControl.leftArrow);
        pass 
    
    def refreshRateChanged(self,selectedIndex,selectedText,previousSelectedIndex,previousSelectedText):
        if self.IsInitDone:
            self.setDisplayApplyButtonState()

    def setDisplayApplyButtonState(self):
        self.displayResolutionApplyButtonState = self.displayHelper.getSelectedRefreshRate() != self.refreshRateSpinControl.getText() or self.displayHelper.getSelectedDisplayResolution() != self.displayResolutionSpinControl.getText()
        self.displayResolutionApplyButton.setEnabled(self.displayResolutionApplyButtonState);

    def setAudioOutputApplyButtonState(self):
        self.audioOutputApplyButtonState = self.audioHelper.getSelectedOutput() != self.audioOutputSpinControl.getText()
        self.audioOutputApplyButton.setEnabled(self.audioOutputApplyButtonState)

    def setAudioOutput(self,selectedIndex):
        if self.IsInitDone:
            retVal = self.audioHelper.setOutput(selectedIndex)
            if retVal:
                confirmDialog = ConfirmDialog()
                ret = confirmDialog.doModal(xbmc.getLocalizedString(31640),ConfirmDialogType.cancelRestart,0)
                del confirmDialog

                if ret == 1:
                    AlphaUIUtils.RestartSystem();
            else:
                confirmDialog = ConfirmDialog()
                ret = confirmDialog.doModal(xbmc.getLocalizedString(31641),ConfirmDialogType.ok,0)
                del confirmDialog
            print self.audioHelper.getSelectedOutput()
            self.audioOutputSpinControl.selectText(self.audioHelper.getSelectedOutput())
            self.setAudioOutputApplyButtonState()
            if self.audioOutputSpinControl.rightArrowEnabled or self.audioOutputSpinControl.leftArrowEnabled:
                self.audioOutputSpinControl.setFocus(True);


    def audioVolumeChanged(self,selectedIndex,selectedText,previousSelectedIndex,previousSelectedText):
        if self.IsInitDone:
            self.setAudioVolumeImage(selectedIndex)
            self.audioHelper.setVolume(selectedIndex)

    def setAudioVolumeImage(self, volumeLevel):
        self.audioVolumeImageControl.setVisible(volumeLevel != 0)            
        self.audioVolumeImageControl.setWidth(180 * volumeLevel/100)
        #print "image size {0} ".format(180 * volumeLevel/100)

    def setAlienFxBrightnessImage(self, brightness):
        #print "setAlienFxBrightnessImage {0}".format(brightness)
        self.alienFxBrightnessImageControl.setVisible(brightness != 0)    

        self.alienFxBrightnessImageControl.setWidth(260 * brightness/100)
        #print "image size {0} ".format(205 * brightness/100)

    ################################# Audio Output Callbacks ###################################
        
    def audioOutputChanged(self,selectedIndex,selectedText,previousSelectedIndex,previousSelectedText):
        if self.IsInitDone:
            self.setAudioOutputApplyButtonState()
    
    def audioOutputUpCallback(self, fromControl):
        #print "audioOutputUpCallback"
        if self.audioOutputApplyButtonState:
            self.setFocus(self.audioOutputApplyButton);
        pass 

    def audioOutputDownCallback(self, fromControl):
        #print "audioOutputDownCallback"
        if self.audioOutputApplyButtonState:
            self.setFocus(self.audioOutputApplyButton);
        pass 

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

    def onClick(self, controlID):
        #print "onClick {0}".format(controlID)
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
        for control in self.spinControls:
            retVal = control.forwardInput(ACTION_SELECT_ITEM, controlID)
            if retVal:
                return;

        if controlID == WIFI_LIST_CONTROL:
            item = self.wifilist.getSelectedItem()
            self.wifihelper.TakeAction(item) 
            self.setFocus(self.wifilist)            
        elif controlID == HDMIIN_BUTTON_CONTROL:
            self.hdmiinhelper.enableHDMIIn()
        elif controlID == VIDEO_APPLY_BUTTON_CONTROL:
            self.setDisplayResolution()
        elif controlID == AUDIO_OUTPUT_APPLY_BUTTON:
            self.setAudioOutput(self.audioOutputSpinControl.selectedIndex)
        pass

    def onFocus(self, controlID):
        # Focus on Wifi Option
        #print "Focus {0}".format(controlID)
        if controlID == NETWORK_LIST_CONTROL:
            self.wifihelper.FillList()
        pass

    def onAction(self, action):
        #print action.getId()
        if action.getId() != ACTION_SELECT_ITEM:
            for control in self.spinControls:
                retVal = control.forwardInput(action.getId(), 0)
                if retVal:
                    #print "returning true"
                    return;

        clickcontrolid = self.getFocusId()

        if action == ACTION_MOVE_UP:
            #print "ACTION_MOVE_UP"
            if clickcontrolid == VIDEO_APPLY_BUTTON_CONTROL:
                if self.refreshRateSpinControl.rightArrowEnabled or self.refreshRateSpinControl.leftArrowEnabled:
                    self.refreshRateSpinControl.setFocus(True);
                elif self.displayResolutionSpinControl.rightArrowEnabled or self.displayResolutionSpinControl.leftArrowEnabled:
                    self.displayResolutionSpinControl.setFocus(True);
                return;
            elif clickcontrolid == AUDIO_OUTPUT_APPLY_BUTTON:
                if self.audioOutputSpinControl.rightArrowEnabled or self.audioOutputSpinControl.leftArrowEnabled:
                    self.audioOutputSpinControl.setFocus(True);
                return;
        elif action == ACTION_MOVE_DOWN:
            #print "ACTION_MOVE_DOWN"
            if clickcontrolid == VIDEO_APPLY_BUTTON_CONTROL:
                if self.displayResolutionSpinControl.rightArrowEnabled or self.displayResolutionSpinControl.leftArrowEnabled:
                    self.displayResolutionSpinControl.setFocus(True);
                elif self.refreshRateSpinControl.rightArrowEnabled or self.refreshRateSpinControl.leftArrowEnabled:
                    self.refreshRateSpinControl.setFocus(True);
                return;
            elif clickcontrolid == AUDIO_OUTPUT_APPLY_BUTTON:
                if self.audioOutputSpinControl.rightArrowEnabled or self.audioOutputSpinControl.leftArrowEnabled:
                    self.audioOutputSpinControl.setFocus(True);
                return;
        elif action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK :
            self.lock.acquire()
            self.IsInitDone = False
            self.lock.release()
            self.alienFXControls.release()
            self.hdmistatechecktimer.cancel()
            self.close()                
            pass

    def onControl(self, control):
        pass

    def refreshTimer(self):
        self.lock.acquire()
        try:
            if self.IsInitDone:
                if self.hdmiinhelper.checkCableConnection():
                    self.hdmiinbutton.setEnabled(True)
                else:
                    self.hdmiinbutton.setEnabled(False)
                self.hdmistatechecktimer = Timer(1.0, self.refreshTimer)
                self.hdmistatechecktimer.start()
        except:
            print("closing refreshTimer")
        finally:          
            self.lock.release()

mywin = SettingsXML("Settings.xml",os.getcwd())
mywin.doModal()
del mywin
