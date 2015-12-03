import time
import random
import xbmc
import AlphaUIUtils

original_state = False
original_state = AlphaUIUtils.IsMouseConnected()
while True:
    try:
        new_state = AlphaUIUtils.IsMouseConnected()
        time.sleep(1)
    except Exception, e:
        xbmc.log(str(e))

    if original_state and not new_state: # Had mouse connected, now we don't
        print "LOST MOUSE"
        xbmc.executebuiltin("ReplaceWindow(4000)")
        break
    elif not original_state and new_state: # Did NOT have mouse connected, but now we do:
        print "GAINED MOUSE"
        xbmc.executebuiltin("ReplaceWindow(4001)")
        break
