import zipfile
import os
kodi_path = '%s\\XBMC\\' % os.environ['APPDATA'] 
dir_path = '%s\\XBMC\\addons\\script.aw.customizations\\' % os.environ['APPDATA'] 
file_path = '%scustomizations.zip' % dir_path
zfile = zipfile.ZipFile(file_path)
zfile.extractall(kodi_path)
