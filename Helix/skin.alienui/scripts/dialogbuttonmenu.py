import xbmc
import xbmcgui

def setWindowSetting(key, value):
    win = xbmcgui.Window(10111)
    win.setProperty(key, value)

try:
    import AlphaUIUtils
 
    if __name__ == '__main__':
        try:
            setWindowSetting("IsAlphaConsoleAcount",str(AlphaUIUtils.IsAlphaConsoleAcount()))
        except:
            setWindowSetting("IsAlphaConsoleAcount","False")     
except:
    setWindowSetting("IsAlphaConsoleAcount","False")  