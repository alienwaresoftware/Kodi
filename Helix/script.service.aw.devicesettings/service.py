try:
    import time
    import xbmc
    import xbmcgui
    import json
    import AlphaUIUtils

    def writeHomeWindowSetting(key, value):
        win = xbmcgui.Window(10000)
        win.setProperty(key, value)
 
    if __name__ == '__main__':
        monitor = xbmc.Monitor()
        lastkeyboardlayouts = [unicode("English QWERTY")]
        lastskintheme = unicode("SKINDEFAULT")
        while True:                
            try:
                writeHomeWindowSetting("IsHDMIInCableConnected",str(AlphaUIUtils.IsHDMICableConnected()))
            except:
                writeHomeWindowSetting("IsHDMIInCableConnected","False")     

            try:
                json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "locale.keyboardlayouts"}, "id": 1 }'))
                if(lastkeyboardlayouts != json_response['result']['value']):
                    lastkeyboardlayouts = json_response['result']['value']
                    keyboardlayouts = None
                    for lastkeyboardlayout in lastkeyboardlayouts:
                        if(not keyboardlayouts):
                            keyboardlayouts = lastkeyboardlayout;
                        else:
                            keyboardlayouts = keyboardlayouts + "|" + lastkeyboardlayout;
                    if(not keyboardlayouts):
                        keyboardlayouts = unicode("English QWERTY")
                    print(keyboardlayouts)
                    AlphaUIUtils.SetKeyboardLayouts(keyboardlayouts)
            except:
                pass

            try:
                json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "lookandfeel.skintheme"}, "id": 1 }'))
                if(lastskintheme != json_response['result']['value']):
                    lastskintheme = json_response['result']['value']
                    if(lastskintheme == unicode("SKINDEFAULT")):
                       lastskintheme = unicode("Red")
                    print(lastskintheme)                        
                    AlphaUIUtils.SetKeyboardColor(lastskintheme)
            except:
                pass

            # Sleep/wait for abort for 3 seconds
            if monitor.waitForAbort(3):
                # Abort was requested while waiting. We should exit
                break
except:
    pass