import zipfile, os, xbmc, xbmcgui
import _winreg as winreg
import traceback

from resources.lib.hivemindinstaller import HivemindInstaller



def regkey_value(path, name="", start_key = None):
    if isinstance(path, str):
        path = path.split("\\")
    if start_key is None:
        start_key = getattr(winreg, path[0])
        return regkey_value(path[1:], name, start_key)
    else:
        subkey = path.pop(0)
    with winreg.OpenKey(start_key, subkey) as handle:
        assert handle
        if path:
            return regkey_value(path, name, handle)
        else:
            desc, i = None, 0
            while not desc or desc[0] != name:
                desc = winreg.EnumValue(handle, i)
                i += 1
            return desc[1]



if (__name__ == "__main__"):
   
    CustomizationsVersion = regkey_value(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName")
    CustomizationsVersionNow = xbmc.getInfoLabel("Skin.String(CustomizationsVersion)")

    
    if CustomizationsVersion != CustomizationsVersionNow:
        kodi_path = '%s\\Kodi\\' % os.environ['APPDATA'] 
        dir_path = '%s\\Kodi\\addons\\service.aw.customizations\\' % os.environ['APPDATA'] 

        zip_file_path = '%scustomizations81.zip' % dir_path
        #check OS version
        #version = readRegistryValue(r'\SOFTWARE\Microsoft\Windows NT\CurrentVersion', 'ProductName')
        version = regkey_value(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName") 
        print "version"
        print version
        if '10' in version: 
            zip_file_path = '%scustomizations10.zip' % dir_path

        zfile = zipfile.ZipFile(zip_file_path)
        zfile.extractall(kodi_path)
        zfile.close()
        xbmc.executebuiltin("Skin.SetString(CustomizationsVersion,"+str(CustomizationsVersion)+")")
    else: pass
    
    monitor = xbmc.Monitor()
    while True:             
        if monitor.waitForAbort(15):
            break
        HivemindInstaller()
        break