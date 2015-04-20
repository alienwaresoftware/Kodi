import zipfile, os, xbmc
kodi_path = '%s\\XBMC\\media\\' % os.environ['APPDATA'] 
dir_path = '%s\\XBMC\\addons\\script.aw.backgrounds\\' % os.environ['APPDATA'] 
zip_file_path = '%sbackgrounds.zip' % dir_path
zfile = zipfile.ZipFile(zip_file_path)
zfile.extractall(kodi_path)
backgroundsversion = xbmc.getInfoLabel("System.AddonVersion(script.aw.backgrounds)")
xbmc.executebuiltin("Skin.SetString(BackgroundsVersion,"+str(backgroundsversion)+")")