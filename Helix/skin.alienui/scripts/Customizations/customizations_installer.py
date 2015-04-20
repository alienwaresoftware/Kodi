import zipfile, os, xbmc
kodi_path = '%s\\Kodi\\' % os.environ['APPDATA'] 
dir_path = '%s\\Kodi\\addons\\skin.alienui\\scripts\\Customizations\\' % os.environ['APPDATA'] 
zip_file_path = '%scustomizations.zip' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
zfile.extractall(kodi_path)
alienuiversion = xbmc.getInfoLabel("System.AddonVersion(skin.alienui)")
xbmc.executebuiltin("Skin.SetString(CustomizationsVersion,"+str(alienuiversion)+")")
