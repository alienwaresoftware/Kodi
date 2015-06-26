import xbmc
import AlphaUIUtils

# Decide which power menu to first show
# Then each powermenu has it's own onload method "update_power_menu.py" 
# that takes care of switching back/forth when mouse connects/disconnects
xbmc.executebuiltin("ActivateWindow(4001)")
