import xbmc
import xbmcgui
import xbmcaddon
import urllib2

__addon__ = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonpath__ = __addon__.getAddonInfo('path').decode('utf-8')
__addonprofile__ = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
__icon__ = __addon__.getAddonInfo('icon')

CATEGORY_ALL = 4294967295
CATEGORY_ADD = 1
CATEGORY_PROGRAM = 2
CATEGORY_VIDEO = 4
CATEGORY_MUSIC = 8
CATEGORY_IMAGE = 16

TYPE_WIN32 = 1
TYPE_WIN8 = 2
TYPE_WEBSITE = 4
TYPE_ADDON = 8

HOME_MENU_BUTTON_LIST = ['HomeMenuButton1', 'HomeMenuButton2', 'HomeMenuButton3', 'HomeMenuButton4', 'HomeMenuButton5']
HOME_MENU_BUTTON_TYPE_LIST = ['HomeMenuButton1Type', 'HomeMenuButton2Type', 'HomeMenuButton3Type', 'HomeMenuButton4Type', 'HomeMenuButton5Type']
HOME_MENU_BUTTON_TYPE_ID_LIST = ['HomeMenuButton1TypeId', 'HomeMenuButton2TypeId', 'HomeMenuButton3TypeId', 'HomeMenuButton4TypeId', 'HomeMenuButton5TypeId']

HOME_MENU_BUTTON_LIST = ['HomeMenuButton1', 'HomeMenuButton2', 'HomeMenuButton3', 'HomeMenuButton4', 'HomeMenuButton5']
HOME_MENU_BUTTON_TYPE_ID_LIST = ['HomeMenuButton1TypeId', 'HomeMenuButton2TypeId', 'HomeMenuButton3TypeId', 'HomeMenuButton4TypeId', 'HomeMenuButton5TypeId']

# Fixes unicode problems
def string_unicode(text, encoding='utf-8'):
    try:
        text = unicode(text, encoding)
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
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonname__, txt)
    # xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)
    print(message.encode("utf-8"))


def dialog_yesno(line1='', line2='', line3=''):
    return (xbmcgui.Dialog().yesno(__addonname__,
                                   line1,
                                   line2,
                                   line3) == 1)


def dialog_ok(line1='', line2='', line3=''):
    return (xbmcgui.Dialog().ok(__addonname__,
                                line1,
                                line2,
                                line3) == 1)


def tohex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))


def downloadFile(url, filePath):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    resource = opener.open(url, timeout=30)
    file = open(filePath, "wb")
    file.write(resource.read())
    file.close()
