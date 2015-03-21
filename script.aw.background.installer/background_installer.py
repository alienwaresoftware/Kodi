import zipfile
import os
import xbmc
background_path = '%s\\Kodi\\Media\\' % os.environ['APPDATA'] 
dir_path = '%s\\Kodi\\addons\\script.aw.background.installer\\' % os.environ['APPDATA'] 
file_path = '%sBackgrounds.zip' % dir_path
zfile = zipfile.ZipFile(file_path)
zfile.extractall(background_path)
