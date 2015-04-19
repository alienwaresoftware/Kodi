import zipfile, os, xbmc
kodi_path = '%s\\XBMC\\' % os.environ['APPDATA'] 
dir_path = '%s\\XBMC\\addons\\script.aw.customizations\\' % os.environ['APPDATA'] 
zip_file_path = '%scustomizations.zip' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
zfile.extractall(kodi_path)
customizationsversion = xbmc.getInfoLabel("System.AddonVersion(script.aw.customizations)")
xbmc.executebuiltin("Skin.SetString(CustomizationsVersion,"+str(customizationsversion)+")")
