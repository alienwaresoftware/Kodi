import zipfile, os, xbmc
kodi_path = '%s\\Kodi\\media\\' % os.environ['APPDATA'] 
dir_path = '%s\\Kodi\\addons\\service.aw.backgrounds\\' % os.environ['APPDATA'] 
zip_file_path = '%sBackgrounds.zip' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
BackgroundsVersion = xbmc.getInfoLabel("System.AddonVersion(service.aw.backgrounds)")
BackgroundsVersionNow = xbmc.getInfoLabel("Skin.String(BackgroundsVersion)")
if BackgroundsVersion > BackgroundsVersionNow:
	zfile.extractall(kodi_path)
	xbmc.executebuiltin("Skin.SetString(BackgroundsVersion,"+str(BackgroundsVersion)+")")
	print "Backgrounds Updated"
else: 
	print "Backgrounds Failed"
	pass