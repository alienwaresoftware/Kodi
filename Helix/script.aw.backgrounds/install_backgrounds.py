import zipfile, os, xbmc
kodi_path = '%s\\Kodi\\media\\' % os.environ['APPDATA'] 
dir_path = '%s\\Kodi\\addons\\script.aw.backgrounds\\' % os.environ['APPDATA'] 
zip_file_path = '%sBackgrounds.zip' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
zfile.extractall(kodi_path)
backgroundsversion = xbmc.getInfoLabel("System.AddonVersion(script.aw.backgrounds)")
xbmc.executebuiltin("Skin.SetString(BackgroundsVersion,"+str(backgroundsversion)+")")