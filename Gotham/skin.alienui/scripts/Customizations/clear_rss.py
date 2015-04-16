import os, xbmc, shutil
kodi_path = '%s\\XBMC\\' % os.environ['APPDATA'] 
dir_path = '%s\\XBMC\\addons\\skin.alienui\\scripts\\Customizations\\' % os.environ['APPDATA'] 
rss_path = '%suserdata\\RssFeeds.xml' % kodi_path
rss_path_bk = '%suserdata\\RssFeeds.xml.bk' % kodi_path
rss_file_path = '%sRssFeeds.xml' % dir_path
shutil.copy2(rss_path, rss_path_bk)
shutil.copy(rss_file_path, rss_path)
xbmc.executebuiltin("Skin.SetBool(RssStatus)")