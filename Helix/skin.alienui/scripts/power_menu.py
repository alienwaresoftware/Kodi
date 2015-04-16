import xbmc
import AlphaUIUtils

# Decide which power menu to first show
# Then each powermenu has it's own onload method "update_power_menu.py" 
# that takes care of switching back/forth when mouse connects/disconnects

has_mouse = False
try:
    has_mouse = AlphaUIUtils.IsMouseConnected()
except Exception, e:
    xbmc.log(str(e))

if has_mouse:
    xbmc.executebuiltin("ReplaceWindow(4001)")
else:
    xbmc.executebuiltin("ReplaceWindow(4001)")
