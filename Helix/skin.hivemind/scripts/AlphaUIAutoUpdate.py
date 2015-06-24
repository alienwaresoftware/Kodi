import ctypes, time
from ctypes import *

import os
import subprocess
import threading
import xbmc, xbmcgui
import _winreg 
import tempfile
import io

import AlphaUIUtils

class AUTO_UPDATE_DATA(Structure):
    _fields_ = [
        ("ApplicationName", c_char*100),
        ("SystemModel", c_char*100),
        ("Platform", c_char*100),
        ("CurrentVersion", c_char*20),
        ("TestingMode", c_bool),
        ("LatestVersion", c_char*20),
        ("HttpVersionLocation", c_char*1000),
        ("PriorityLevel", c_int)]

AlphaUIAutoUpdateDLL = CDLL('AlphaUIAutoUpdateLibrary.dll')
isThereAnyUpdate = AlphaUIAutoUpdateDLL.IsThereAnyUpdate
isThereAnyUpdate.restype = c_int
isThereAnyUpdate.argtypes = [POINTER(AUTO_UPDATE_DATA)]
 
class AutoUpdateClass(object):

    def __init__(self, win):
        self._win = win          

    def installationOk(self):
        result = True
        logfile = os.path.join(tempfile.gettempdir(), "AlphaUIInstallation.log");
        if (os.path.exists(logfile)):
            f = open(logfile, "rb")
            try:
                byte = f.read(1)
                result = byte == '0';
            finally:
                f.close()

            os.remove(logfile)
        return result

    def getAlphaUIRegistryInfo(self, registryEntries):
        result = True
        try:   
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\AlphaUI", 0, _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY)
            installPath = _winreg.QueryValueEx(key, "InstallationPath")[0]
            version = _winreg.QueryValueEx(key, "Version")[0]            
            registryEntries.append(installPath.encode('utf-8'))
            registryEntries.append(version.encode('utf-8'))     
            
            try:
                testingMode = _winreg.QueryValueEx(key, "TestingMode")[0]
                if (testingMode == b'Test'):
                    registryEntries.append(True) 
                else:
                    registryEntries.append(False) 
            except:
                registryEntries.append(False) 
                                                         
        except WindowsError:   
            result = False   
                                               
        _winreg.CloseKey(key)
        return result

    def isThereAnyUpdates(self, autoUpdateDataResult):
        autoUpdateData = AUTO_UPDATE_DATA(b'AlphaUI', b'ASM100', b'Desktopx64', 
                                          autoUpdateDataResult[0], #current version
                                          autoUpdateDataResult[1]  #testing mode true or false
                                          )
        result = isThereAnyUpdate(byref(autoUpdateData))    
        if (result == 0 and autoUpdateData.HttpVersionLocation != b''):
            autoUpdateDataResult.append(autoUpdateData.PriorityLevel)
            autoUpdateDataResult.append(autoUpdateData.LatestVersion.decode('utf-8'))
            autoUpdateDataResult.append(autoUpdateData.HttpVersionLocation.decode('utf-8'))
            return True
        return False

    def showMessageIfCriticalUpdates(self):
        registryEntries = []
        if (self.getAlphaUIRegistryInfo(registryEntries) and len(registryEntries) >= 3):
            if (self.installationOk() == False):
                ctrl = self._win.getControl(1001)
                ctrl.setPosition((1280-460)/2, ctrl.getY())                    
            else:
                autoUpdateDataResult = []
                autoUpdateDataResult.append(registryEntries[1]) #current version
                autoUpdateDataResult.append(registryEntries[2]) #testing mode true or false              
                if (self.isThereAnyUpdates(autoUpdateDataResult)):
                    if (len(autoUpdateDataResult) >= 3 and autoUpdateDataResult[2] >= 5): #check priority level
                        ctrl = self._win.getControl(1002)
                        ctrl.setPosition(20, ctrl.getY())
                        #dialog = xbmcgui.Dialog()
                        #dialog.notification('System Update Available', str(ctrl), xbmcgui.NOTIFICATION_INFO, 6000)

    def showMessageAndLaunchUpdates(self):
        registryEntries = []
        if (self.getAlphaUIRegistryInfo(registryEntries)):
            #Screen center 640x360
            ctrl = xbmcgui.ControlImage(615, 335, 50, 50, 'special://skin/media/alienware/loading.gif')
            self._win.addControl(ctrl)
            launcherPath = registryEntries[0] + '\\AlphaUIAutoUpdateManager.exe'
            subprocess.Popen(launcherPath)
        else:
            AlphaUIUtils.ShutdownSystem()

    def showVersionNumber(self):
        registryEntries = []
        if (self.getAlphaUIRegistryInfo(registryEntries)):
            ctrl = xbmcgui.ControlLabel(22, 640, 100, 20, 'v. ' + registryEntries[1], 'x_small_item', '0xFFFF0000')
            self._win.addControl(ctrl)
