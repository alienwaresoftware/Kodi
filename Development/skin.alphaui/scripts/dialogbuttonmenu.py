import xbmc
import xbmcgui
import os;

def setWindowSetting(key, value):
    win = xbmcgui.Window(10111)
    win.setProperty(key, value)

try:
    import AlphaUIUtils

    if __name__ == '__main__':
        try:
            setWindowSetting("IsAlphaConsoleAcount",str(AlphaUIUtils.IsAlphaConsoleAcount()))
            #setWindowSetting("LaunchFirtTime",True)
        except:
            setWindowSetting("IsAlphaConsoleAcount","False")     
except:
    setWindowSetting("IsAlphaConsoleAcount","False")  

try:
  if os.environ.get( "USERNAME" ) == "Alpha Console":
      setWindowSetting("IsAlphaConsoleAcount","True")
except:
  pass;