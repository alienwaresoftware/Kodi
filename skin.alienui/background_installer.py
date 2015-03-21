import zipfile
import os
import xbmc
background_path = '%s\\XBMC\\Media\\' % os.environ['APPDATA'] 
dir_path = '%s\\XBMC\\addons\\skin.alienui\\' % os.environ['APPDATA'] 
file_path = '%sBackgrounds.zip' % dir_path
zfile = zipfile.ZipFile(file_path)
zfile.extractall(background_path)
