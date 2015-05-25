import xbmc
import xbmcgui
import common
import os
import _winreg
import subprocess
from common import log
from common import localize
from common import dialog_yesno
from common import dialog_ok
from common import tohex

from waitdialog import WaitDialogHelper

__addon__        = common.__addon__
__addonversion__ = common.__addonversion__
__addonname__    = common.__addonname__
__addonpath__    = common.__addonpath__
__icon__         = common.__icon__

class HiveInstaller:
    def __init__(self):
        currentHiveVersion = self.getCurrentHiveVersion()
        newHiveVersion = self.getNewHiveVersion()
        
        if(currentHiveVersion and newHiveVersion):
            if (cmp(newHiveVersion,currentHiveVersion) > 0):
                log(('Updating Hive version'))
                self.installHive(False)
                return
        elif not currentHiveVersion and newHiveVersion:
            log(('Installing new Hive version'))
            self.installHive(True)
            return
        elif not newHiveVersion:
            log(('Hive hivesetup.exe not found'))
            return

        log(('Latest Hive version installed'))

    def getCurrentHiveVersion(self):
        key = None
        try:   
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Hive", 0, _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY)
            version = _winreg.QueryValueEx(key, "Version")[0]            
            versionAsNumbers = [int(numeric_string) for numeric_string in version.split('.')]
            log(('Current Hive version = %d.%d.%d.%d') % (versionAsNumbers[0], versionAsNumbers[1], versionAsNumbers[2], versionAsNumbers[3]))
            return versionAsNumbers;
        except WindowsError:   
            pass
        finally:
            if (key): _winreg.CloseKey(key)                                                       

        return None

    def getNewHiveVersion(self):
        try:
            self.setupPath = os.path.join(__addonpath__,'resources','lib','hivesetup.exe')
            log(('Hive setup path = %s') % self.setupPath)
            version = self.getFileVersion(self.setupPath)
            log(('New Hive version = %d.%d.%d.%d') % (version[0], version[1], version[2], version[3]))
            return version;
        except:
            pass

        return None

    def installHive(self,isFresh):
        message = ''
        if(isFresh):
            if(dialog_yesno(localize(33000),localize(33001))):
                waitDialog = WaitDialogHelper().create()
                try:
                    scriptPath = os.path.join(__addonpath__,'resources','lib','launchsetup.vbs')
                    log(('Hive setup launcher path = %s') % scriptPath)
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    exitCode = subprocess.call(["cscript.exe", scriptPath, self.setupPath], startupinfo=si)
                    log('Hive setup exit code = ' + str(tohex(exitCode, 32)))

                    if (exitCode == 0):
                        if(dialog_yesno(localize(33005),localize(33006))):
                            si = subprocess.STARTUPINFO()
                            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            subprocess.call(["shutdown.exe", "/r", "/t", "1" ,"/f"], startupinfo=si)
                    else:
                        dialog_ok(localize(33003),localize(33004) + str(tohex(exitCode, 32)))
                except:
                    pass
                waitDialog.close()
        else:
            if(dialog_yesno(localize(33007),localize(33008))):
                waitDialog = WaitDialogHelper().create()
                #try:
                import AlphaUIUtils
                setupPath = os.path.join(__addonpath__,'resources','lib')
                log(('Hive setup path = %s') % setupPath)

                retValue = AlphaUIUtils.LaunchHiveSetup(setupPath)
                log('Hive setup return code = ' + str(retValue))

                if (retValue):
                    if(dialog_yesno(localize(33005),localize(33006))):
                        si = subprocess.STARTUPINFO()
                        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        subprocess.call(["shutdown.exe", "/r", "/t", "1" ,"/f"], startupinfo=si)
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
        
