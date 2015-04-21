import zipfile, os, xbmc
kodi_path = '%s\\Kodi\\addons\\skin.alienui\\media\\' % os.environ['APPDATA'] 
dir_path = '%s\\Kodi\\addons\\script.aw.themes\\' % os.environ['APPDATA'] 
zip_file_path = '%sthemes.zip' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
zfile.extractall(kodi_path)
SkinVersion = xbmc.getInfoLabel("System.AddonVersion(Skin.AlienUI)")
xbmc.executebuiltin("Skin.SetString(SkinVersion,"+str(SkinVersion)+")")
ThemeVersion = xbmc.getInfoLabel("System.AddonVersion(script.aw.themes)")
xbmc.executebuiltin("Skin.SetString(ThemeVersion,"+str(ThemeVersion)+")")