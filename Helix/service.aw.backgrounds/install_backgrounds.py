import zipfile, os, xbmc
kodi_path = '%s\\Kodi\\media\\' % os.environ['APPDATA'] 
dir_path = '%s\\Kodi\\addons\\service.aw.backgrounds\\' % os.environ['APPDATA'] 
zip_file_path = '%sBackgrounds.zip' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
backgroundsversion = xbmc.getInfoLabel("System.AddonVersion(service.aw.backgrounds)")
backgroundsversionNow = xbmc.getInfoLabel("Skin.String(backgroundsversion)")
if backgroundsversion > backgroundsversionNow:
	zfile.extractall(kodi_path)
	xbmc.executebuiltin("Skin.SetString(BackgroundsVersion,"+str(backgroundsversion)+")")
else: pass