import zipfile, os, xbmc
kodi_path = '%s\\XBMC\\addons\\skin.alienui\\media\\' % os.environ['APPDATA'] 
dir_path = '%s\\XBMC\\addons\\script.aw.themes\\' % os.environ['APPDATA'] 
zip_file_path = '%sthemes.zip' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
zfile.extractall(kodi_path)
themesversion = xbmc.getInfoLabel("System.AddonVersion(script.aw.themes)")
xbmc.executebuiltin("Skin.SetString(ThemesVersion,"+str(themesversion)+")")
