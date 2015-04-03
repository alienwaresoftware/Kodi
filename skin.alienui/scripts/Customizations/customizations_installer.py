import zipfile, os, xbmc
kodi_path = '%s\\XBMC\\' % os.environ['APPDATA'] 
dir_path = '%s\\XBMC\\addons\\skin.alienui\\scripts\\Customizations\\' % os.environ['APPDATA'] 
zip_file_path = '%scustomizations.zip' % dir_path
advanced_path = '%suserdata\\advancedsettings.xml' % kodi_path
advance_file_path = '%sadvancedsettings.xml' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
zfile.extractall(kodi_path)
if os.path.exists(advanced_path):
	pass
else: 
	os.rename(advance_file_path, advanced_path)
alienuiversion = xbmc.getInfoLabel("System.AddonVersion(skin.alienui)")
xbmc.executebuiltin("Skin.SetString(CustomizationsVersion,"+str(alienuiversion)+")")