import xbmc
import xbmcgui
import common
import os
import _winreg
import subprocess
import time
from common import log
from common import localize
from common import dialog_yesno
from common import dialog_ok
from common import tohex

from waitdialog import WaitDialogHelper

__addon__        = common.__addon__
__addonid__ = common.__addonid__
__addonversion__ = common.__addonversion__
__addonname__    = common.__addonname__
__addonpath__    = common.__addonpath__
__icon__         = common.__icon__

class HivemindInstaller:
    def __init__(self):
        currentHivemindVersion = self.getCurrentHivemindVersion()
        newHivemindVersion = self.getNewHivemindVersion()


        if(currentHivemindVersion and newHivemindVersion):
            if (cmp(newHivemindVersion,currentHivemindVersion) > 0):
                log(('Updating HiveMind version'))
                xbmc.executebuiltin('Skin.SetBool(IsCoreComponentInstalled)')
                xbmcgui.Window(10004).setProperty(__addonid__ + '.isComponentInstalled', "True")
                self.installHivemind(False)
                return
        elif not currentHivemindVersion and newHivemindVersion:
            log(('Installing new HiveMind version'))
            xbmc.executebuiltin('Skin.Reset(IsCoreComponentInstalled)')
            xbmcgui.Window(10004).setProperty(__addonid__ + '.isComponentInstalled', "False")
            self.installHivemind(True)
            return
        elif not newHivemindVersion:
            log(('hivemindsetup.exe not found'))
            xbmc.executebuiltin('Skin.Reset(IsCoreComponentInstalled)')
            xbmcgui.Window(10004).setProperty(__addonid__ + '.isComponentInstalled', "False")
            return

        xbmc.executebuiltin('Skin.SetBool(IsCoreComponentInstalled)')
        xbmcgui.Window(10004).setProperty(__addonid__ + '.isComponentInstalled', "True")

        log(('Latest HiveMind version installed'))
        

    def getCurrentHivemindVersion(self):
        key = None
        try:   
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\HiveMind", 0, _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY)
            version = _winreg.QueryValueEx(key, "Version")[0]            
            versionAsNumbers = [int(numeric_string) for numeric_string in version.split('.')]
            log(('Current HiveMind version = %d.%d.%d.%d') % (versionAsNumbers[0], versionAsNumbers[1], versionAsNumbers[2], versionAsNumbers[3]))
            return versionAsNumbers;
        except WindowsError:   
            pass
        finally:
            if (key): _winreg.CloseKey(key)                                                       

        return None

    def getNewHivemindVersion(self):
        try:
            self.setupPath = os.path.join(__addonpath__,'resources','lib','hivemindsetup.exe')
            log(('HiveMind setup path = %s') % self.setupPath)
            version = self.getFileVersion(self.setupPath)
            log(('New HiveMind version = %d.%d.%d.%d') % (version[0], version[1], version[2], version[3]))
            return version;
        except:
            pass

        return None

    def installHivemind(self,isFresh):
        message = ''
        if(isFresh):
            ret = dialog_yesno(localize(33000),localize(33001))
            log("Dialog YesNo -> {0}".format(ret))
            if(ret):
                waitDialog = WaitDialogHelper().create()
                try:
                    scriptPath = os.path.join(__addonpath__,'resources','lib','launchsetup.vbs')
                    log(('HiveMind setup launcher path = %s') % scriptPath)
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    exitCode = subprocess.call(["cscript.exe", scriptPath, self.setupPath], startupinfo=si)
                    log('HiveMind setup exit code = ' + str(tohex(exitCode, 32)))

                    if (exitCode == 0):
                        if(dialog_yesno(localize(33005),localize(33006))):
                            xbmc.executebuiltin('Skin.SetBool(IsCoreComponentInstalled)')

                            si = subprocess.STARTUPINFO()
                            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            subprocess.call(["shutdown.exe", "/r", "/t", "0" ,"/f"], startupinfo=si)
                    else:
                        dialog_ok(localize(33003),localize(33004) + str(tohex(exitCode, 32)))
                except:
                    pass
                waitDialog.close()
        else:
            waitDialog = WaitDialogHelper().create()
            #try:
            import AlphaUIUtils
            setupPath = os.path.join(__addonpath__,'resources','lib')
            log(('HiveMind setup path = %s') % setupPath)

            retValue = AlphaUIUtils.LaunchHivemindSetup(setupPath)
            log('HiveMind setup return code = ' + str(retValue))

            if (retValue):
                if(dialog_yesno(localize(33005),localize(33006))):
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    subprocess.call(["shutdown.exe", "/r", "/t", "0" ,"/f"], startupinfo=si)
            else:
                dialog_ok(localize(33003))
            #except:
                # dialog_ok(localize(33003))
            waitDialog.close()        

    def getFileVersion(self,filename):
        from ctypes.wintypes import (
            windll, sizeof, WinError, byref, POINTER, cast, c_char, Structure, c_uint,
            pointer, BOOL, DWORD, LPVOID, LPCVOID, LPCWSTR,
        )

        class VS_FIXEDFILEINFO(Structure):
            _fields_ = [
                ("dwSignature", DWORD), # will be 0xFEEF04BD
                ("dwStrucVersion", DWORD),
                ("dwFileVersionMS", DWORD),
                ("dwFileVersionLS", DWORD),
                ("dwProductVersionMS", DWORD),
                ("dwProductVersionLS", DWORD),
                ("dwFileFlagsMask", DWORD),
                ("dwFileFlags", DWORD),
                ("dwFileOS", DWORD),
                ("dwFileType", DWORD),
                ("dwFileSubtype", DWORD),
                ("dwFileDateMS", DWORD),
                ("dwFileDateLS", DWORD)
        ]

        PUINT = POINTER(c_uint)
        LPDWORD = POINTER(DWORD)

        GetFileVersionInfoSizeW = windll.version.GetFileVersionInfoSizeW
        GetFileVersionInfoSizeW.restype = DWORD
        GetFileVersionInfoSizeW.argtypes = [LPCWSTR, LPDWORD]
        GetFileVersionInfoSize = GetFileVersionInfoSizeW # alias

        GetFileVersionInfoW = windll.version.GetFileVersionInfoW
        GetFileVersionInfoW.restype = BOOL
        GetFileVersionInfoW.argtypes = [LPCWSTR, DWORD, DWORD, LPVOID]
        GetFileVersionInfo = GetFileVersionInfoW # alias

        VerQueryValueW = windll.version.VerQueryValueW
        VerQueryValueW.restype = BOOL
        VerQueryValueW.argtypes = [LPCVOID, LPCWSTR, POINTER(LPVOID), PUINT]
        VerQueryValue = VerQueryValueW # alias

        filename = unicode(filename)
    
        dwLen  = GetFileVersionInfoSize(filename, None)
        if not dwLen :
            raise WinError()
        lpData = (c_char * dwLen)()
        if not GetFileVersionInfo(filename, 0, sizeof(lpData), lpData):
            raise WinError()
        uLen = c_uint()
        lpffi = POINTER(VS_FIXEDFILEINFO)()
        lplpBuffer = cast(pointer(lpffi), POINTER(LPVOID))
        if not VerQueryValue(lpData, u"\\", lplpBuffer, byref(uLen)):
            raise WinError()
        ffi = lpffi.contents
        return [int(ffi.dwFileVersionMS >> 16),
            int(ffi.dwFileVersionMS & 0xFFFF),
            int(ffi.dwFileVersionLS >> 16),
            int(ffi.dwFileVersionLS & 0xFFFF)]
        
