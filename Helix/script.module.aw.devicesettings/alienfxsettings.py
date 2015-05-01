import xbmc
import xbmcgui
import xbmcaddon
import sys
import thread
import dialogselect

from resources.lib.spincontrol import SpinControl
from resources.lib.alienfxlights import AlienFXLights


ALIENFX_HEAD_GROUP_CONTROL = 106
ALIENFX_HEAD_SPIN_LEFT = 107
ALIENFX_HEAD_LABEL_CONTROL = 108
ALIENFX_HEAD_SPIN_RIGHT = 109
ALIENFX_HEAD_LEFT_FOCUS = 110
ALIENFX_HEAD_RIGHT_FOCUS = 111

ALIENFX_CORNER_GROUP_CONTROL = 114
ALIENFX_CORNER_SPIN_LEFT = 115
ALIENFX_CORNER_LABEL_CONTROL = 116
ALIENFX_CORNER_SPIN_RIGHT = 117
ALIENFX_CORNER_LEFT_FOCUS = 118
ALIENFX_CORNER_RIGHT_FOCUS = 119

ALIENFX_BRIGHTNESS_GROUP_CONTROL = 124
ALIENFX_BRIGHTNESS_SPIN_LEFT = 125
ALIENFX_BRIGHTNESS_IMAGE_CONTROL = 126
ALIENFX_BRIGHTNESS_LABEL_CONTROL = 127
ALIENFX_BRIGHTNESS_SPIN_RIGHT = 128
ALIENFX_BRIGHTNESS_LEFT_FOCUS = 129
ALIENFX_BRIGHTNESS_RIGHT_FOCUS = 130

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

class AlienFXSettingsWindow(xbmcgui.WindowXML):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback=True):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.IsInitDone = False
        self.isClosed = False

    def onInit(self):
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

        self.lock = thread.allocate_lock()

        self.IsInitDone = True

    def isComplete(self): 
        return self.isClosed 

    def onAction(self, action):
        #print action.getId()
        if action.getId() != ACTION_SELECT_ITEM:
            for control in self.spinControls:
                retVal = control.forwardInput(action.getId(), 0)
                if retVal:
                    #print "returning true"
                    return;

        #print "Action Id -> {0}".format(action.getId())
        if (action.getId() == ACTION_PREVIOUS_MENU or action.getId() == ACTION_NAV_BACK ):
            self.lock.acquire()
            self.IsInitDone = False
            self.lock.release()
            self.alienFXControls.release()
            self.close()
        elif (action.getId() == ACTION_SELECT_ITEM or action.getId() == ACTION_MOUSE_LEFT_CLICK):
            #print "Focused Item is {0}".format(self.getFocusId())
            pass

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

        pass       

    def close(self):
        self.isClosed = True 
        xbmcgui.WindowXML.close(self)   
        

    def setAlienFxBrightnessImage(self, brightness):
        #print "setAlienFxBrightnessImage {0}".format(brightness)
        self.alienFxBrightnessImageControl.setVisible(brightness != 0)    

        self.alienFxBrightnessImageControl.setWidth(260 * brightness/100)
        #print "image size {0} ".format(205 * brightness/100)

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



alienFXSettingWindow = AlienFXSettingsWindow("awalienfxsettings.xml",__addon__.getAddonInfo('path'), "Default")
alienFXSettingWindow.show()
monitor = xbmc.Monitor()
while not alienFXSettingWindow.isComplete(): 
    if monitor.waitForAbort(2):
        # Abort was requested while waiting. We should exit
        break
    if (xbmcgui.getCurrentWindowId() == 10000):
        break

del alienFXSettingWindow
