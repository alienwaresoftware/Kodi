import xbmcgui
import AlphaUIUtils
from AlphaUIAutoUpdate import AutoUpdateClass

AlphaUIUtils.CloseLauncher()
autoUpdateClass = AutoUpdateClass(xbmcgui.Window(xbmcgui.getCurrentWindowId()))
if(autoUpdateClass.installationOk()):
    # If the last update was a success, make sure to never show the 'update failed' box
    ctrl = autoUpdateClass._win.getControl(1001)
    ctrl.setPosition(-1460, ctrl.getY())                    

autoUpdateClass.showVersionNumber()
autoUpdateClass.showMessageIfCriticalUpdates()
