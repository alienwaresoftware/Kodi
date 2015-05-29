import zipfile, os, xbmc

if (__name__ == "__main__"):
    kodi_path = '%s\\Kodi\\addons\\skin.hive\\media\\' % os.environ['APPDATA'] 
    dir_path = '%s\\Kodi\\addons\\service.aw.themes\\' % os.environ['APPDATA'] 
    zip_file_path = '%sthemes.zip' % dir_path
    zfile = zipfile.ZipFile(zip_file_path)

    SkinVersion = xbmc.getInfoLabel("System.AddonVersion(Skin.hive)")
    ThemeVersion = xbmc.getInfoLabel("System.AddonVersion(service.aw.themes)")
    SkinVersionNow = xbmc.getInfoLabel("Skin.String(SkinVersion)")
    ThemeVersionNow = xbmc.getInfoLabel("Skin.String(ThemeVersion)")
    if ThemeVersion > ThemeVersionNow:
        zfile.extractall(kodi_path)
        zfile.close()
        xbmc.executebuiltin("Skin.SetString(ThemeVersion,"+str(ThemeVersion)+")")
    elif SkinVersion > SkinVersionNow:
        zfile.extractall(kodi_path)
        zfile.close()
        xbmc.executebuiltin("Skin.SetString(SkinVersion,"+str(SkinVersion)+")")
    else: pass