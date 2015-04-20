import zipfile, os, xbmc
kodi_path = '%s\\Kodi\\' % os.environ['APPDATA'] 
dir_path = '%s\\Kodi\\addons\\script.aw.customizations\\' % os.environ['APPDATA'] 
zip_file_path = '%scustomizations.zip' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
zfile.extractall(kodi_path)
CustomizationsVersion = xbmc.getInfoLabel("System.AddonVersion(script.aw.customizations)")
xbmc.executebuiltin("Skin.SetString(CustomizationsVersion,"+str(CustomizationsVersion)+")")