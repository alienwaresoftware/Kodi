import xbmc
import xbmcgui
import xbmcaddon
import sys
import dialogselect

from resources.lib.audiohelper import AudioHelper

AUDIO_SOURCE_LABLE_CONTROL = 106
AUDIO_SOURCE_ACTION_CONTROL = 107
AUDIO_VOLUME_LABLE_CONTROL = 110
AUDIO_VOLUME_SLIDER_CONTROL = 111

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

class AudioSettingsWindow(xbmcgui.WindowXML):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback=True):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.isClosed = False

    def onInit(self):
        self.audioSourceLabelControl = self.getControl(AUDIO_SOURCE_LABLE_CONTROL)
        self.audioHelper = AudioHelper()        

        self.audioSourceLabelControl.setLabel(self.audioHelper.getSelectedOutput())

        self.audioVolumeLabelControl = self.getControl(AUDIO_VOLUME_LABLE_CONTROL)
        self.audioVolumeSliderControl = self.getControl(AUDIO_VOLUME_SLIDER_CONTROL)

        volume = self.audioHelper.getVolume()
        self.audioVolumeSliderControl.setPercent(volume)
        self.audioVolumeLabelControl.setLabel("{0}%".format(volume))

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
            if (self.getFocusId() == AUDIO_SOURCE_ACTION_CONTROL):
                dialog = dialogselect.SelectDialog("awdialogselect.xml",__addon__.getAddonInfo('path'), "Default")
                dialog._title = __language__(33015)
                dialog._optionList = self.audioHelper.getOutputs()
                dialog.doModal()
                if (dialog._selectedOptionPosition is not None):
                    if (self.audioHelper.setOutput(dialog._selectedOptionPosition)):
                        self.audioSourceLabelControl.setLabel(self.audioHelper.getSelectedOutput())
                        xbmcgui.Dialog().notification(__language__(33020), __language__(33021), xbmcgui.NOTIFICATION_INFO, 15000)
                    else:
                        xbmcgui.Dialog().notification(__language__(33018), __language__(33019), xbmcgui.NOTIFICATION_ERROR, 15000)
                del dialog 
        elif (self.getFocusId() == AUDIO_VOLUME_SLIDER_CONTROL):
            if(action.getId() == ACTION_MOVE_LEFT or action.getId() == ACTION_MOVE_RIGHT or action.getId() == ACTION_MOUSE_DRAG):
                volume = int(self.audioVolumeSliderControl.getPercent())
                self.audioVolumeLabelControl.setLabel("{0}%".format(volume))
                self.audioHelper.setVolume(volume)

    def close(self):
        self.isClosed = True 
        xbmcgui.WindowXML.close(self)    

audioSettingsWindow = AudioSettingsWindow("awaudiosettings.xml",__addon__.getAddonInfo('path'), "Default")
audioSettingsWindow.show()
monitor = xbmc.Monitor()
while not audioSettingsWindow.isComplete(): 
    if monitor.waitForAbort(2):
        # Abort was requested while waiting. We should exit
        break
    if (xbmcgui.getCurrentWindowId() == 10000):
        break

del audioSettingsWindow
