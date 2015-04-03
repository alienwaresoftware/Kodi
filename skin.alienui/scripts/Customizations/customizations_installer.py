import zipfile, os, xbmc, time
kodi_path = '%s\\XBMC\\' % os.environ['APPDATA'] 
dir_path = '%s\\XBMC\\addons\\skin.alienui\\scripts\\Customizations\\' % os.environ['APPDATA'] 
file_path = '%scustomizations.zip' % dir_path
zfile = zipfile.ZipFile(file_path)
zfile.extractall(kodi_path)
alienuiversion = xbmc.getInfoLabel("System.AddonVersion(skin.alienui)")
xbmc.executebuiltin("Skin.SetString(CustomizationsVersion,"+str(alienuiversion)+")")