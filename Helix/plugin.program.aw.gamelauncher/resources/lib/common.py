import xbmc
import xbmcgui
import xbmcaddon

__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__addonpath__    = __addon__.getAddonInfo('path').decode('utf-8')
__addonprofile__ = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode('utf-8')
__icon__         = __addon__.getAddonInfo('icon')

# Fixes unicode problems
def string_unicode(text, encoding='utf-8'):
    try:
        text = unicode( text, encoding )
    except:
        pass
    return text

def normalize_string(text):
    try:
        text = unicodedata.normalize('NFKD', string_unicode(text)).encode('ascii', 'ignore')
    except:
        pass
    return text

def localize(id):
    string = normalize_string(__addon__.getLocalizedString(id))
    return string

def log(txt):
    if isinstance (txt,str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonname__, txt)
    #xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)
    print(message.encode("utf-8"))

def dialog_yesno(line1 = '', line2 = '', line3 = ''):
    return (xbmcgui.Dialog().yesno(__addonname__,
                                  line1,
                                  line2,
                                  line3) == 1)

def dialog_ok(line1 = '', line2 = '', line3 = ''):
    return (xbmcgui.Dialog().ok(__addonname__,
                                  line1,
                                  line2,
                                  line3) == 1)

def tohex(val, nbits):
  return hex((val + (1 << nbits)) % (1 << nbits))
