import AlphaUIUtils
import xbmc
import xbmcgui
import sys

from confirmdialog import ConfirmDialog
from confirmdialog import ConfirmDialogType

class DisplayHelper(object):
    def __init__(self):
        self.display = AlphaUIUtils.GetDisplay()
        self.modes = self.display.Modes

        for mode in self.modes:
            if mode.Name == self.getSelectedDisplayResolution():
                self.oldMode = mode
                break
        self.oldRefreshRateIndex = self.oldMode.RefreshRates.index(self.getSelectedRefreshRate())
        pass

    def getAllDisplayResolutions(self):
        modes = []
        for mode in self.modes:
            modes.append(mode.Name)

        return modes

    def getAllRefreshRates(self):
        for mode in self.modes:
            if mode.Name == self.getSelectedDisplayResolution():
                return mode.RefreshRates              

    def getRefreshRates(self,index):
        return self.modes[index].RefreshRates

    def getSelectedDisplayResolution(self):
        return self.display.CurrentModeName        

    def getSelectedRefreshRate(self):
        return self.display.CurrentRefreshRate     

    def setMode(self,modeIndex,rateIndex):        
        try:
            selectedMode = self.modes[modeIndex]
            self.display.SetMode(selectedMode,rateIndex)
            confirmDialog = ConfirmDialog()
            ret = confirmDialog.doModal(xbmc.getLocalizedString(31617),ConfirmDialogType.yesNo,15)
            del confirmDialog
            if ret == 0:
                self.oldMode = selectedMode
                self.oldRefreshRateIndex = rateIndex
                return True
            else:
                #print "old mode {0} , old refreshrateindex {1}".format(self.oldMode.Name, self.oldRefreshRateIndex)
                self.display.SetMode(self.oldMode,self.oldRefreshRateIndex)
                return False
        except:
            print "displayhelper.py::setMode:", sys.exc_info()[0]
