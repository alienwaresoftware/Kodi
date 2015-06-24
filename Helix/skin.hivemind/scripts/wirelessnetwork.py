import xbmc
import xbmcgui
import AlphaUINetworkUtils
from confirmdialog import ConfirmDialog
from confirmdialog import ConfirmDialogType


class WirelessNetwork(object):
    def __init__(self, wifinetwork, uuid):
        self.wifinetworkobj = wifinetwork
        self.ssid  = self.wifinetworkobj.SSID
        self.connected = self.wifinetworkobj.Connected
        self.securityenabled = self.wifinetworkobj.SecurityEnabled
        self.signal = self.wifinetworkobj.SignalQuality
        self.uuid = uuid

        if self.signal <= 20:
            self.signalimage = "wireless1.png"
        elif self.signal <= 40:
            self.signalimage = "wireless2.png"
        elif self.signal <= 60:
            self.signalimage = "wireless3.png"
        elif self.signal <= 80:
            self.signalimage = "wireless4.png"
        else:
            self.signalimage = "wireless5.png"

    def connect(self, passwd):
        self.wifinetworkobj.Connect(unicode(passwd))

    def connectNoPassword(self):
        self.wifinetworkobj.Connect()

    def disconnect(self):
        self.wifinetworkobj.Disconnect()


class WiFiHelper(object):
    def __init__(self, wifilistcontrol):
        self.wifilistcontrol = wifilistcontrol

    def FillList(self):
        self.wifilistcontrol.reset()
        wifis = AlphaUINetworkUtils.WiFis()
        self.allnetworks = []

        for wifi in wifis:
            networks = wifi.Networks()
            for network in networks:
                if network.SSID != "":
                    if network.ProfileName != "":
                        self.allnetworks.append(WirelessNetwork(network, wifi.UUID))
            for network in networks:
                if network.SSID != "":
                    existingNetwork = [obj for obj in self.allnetworks if obj.ssid == network.SSID]
                    if not existingNetwork:
                        self.allnetworks.append(WirelessNetwork(network, wifi.UUID))
            wifi.Scan()

        for i,network in enumerate(self.allnetworks):
            li = xbmcgui.ListItem(network.ssid,"",network.signalimage)
            li.setProperty('Connected',str(network.connected))            
            li.setProperty('SecurityEnabled',str(network.securityenabled))
            li.setProperty('index',str(i))

            self.wifilistcontrol.addItem(li)

    def TakeAction(self, item):
        dialog = xbmcgui.Dialog()
        selectednetwork = self.allnetworks[int(item.getProperty('index'))]
        isaction = False
        isConnected = selectednetwork.connected
        self.activeUuid = selectednetwork.uuid

        if not selectednetwork.connected:            
            try:
                if selectednetwork.securityenabled:
                    passwd = dialog.input(xbmc.getLocalizedString(31714).format(selectednetwork.ssid),type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
                    if passwd != "":
                        selectednetwork.connect(passwd)
                        isaction = True
                else:
                    selectednetwork.connectNoPassword()
                    isaction = True
            except:
                dialog.notification(xbmc.getLocalizedString(31715), xbmc.getLocalizedString(31716), xbmcgui.NOTIFICATION_ERROR, 10000)

        else:
            try:
                ret = dialog.yesno(xbmc.getLocalizedString(31717), xbmc.getLocalizedString(31718).format(selectednetwork.ssid))
                if ret:
                    selectednetwork.disconnect()
                    isaction = True
            except:
                dialog.notification(xbmc.getLocalizedString(31715), xbmc.getLocalizedString(31719), xbmcgui.NOTIFICATION_ERROR, 10000)

        if isaction:
            confirmDialog = ConfirmDialog()
            if isConnected:
                dialogStr = xbmc.getLocalizedString(31729) + xbmc.getLocalizedString(31724)
            else:
                dialogStr = xbmc.getLocalizedString(31729) + xbmc.getLocalizedString(31728)

            ret = confirmDialog.doModalWithCallback(dialogStr,ConfirmDialogType.ok,20,self.RefreshWifiState)
            del confirmDialog
            wifis = AlphaUINetworkUtils.WiFis()

            for wifi in wifis:
                if wifi.UUID == self.activeUuid:
                    if isConnected:
                        if wifi.State != 4 and wifi.State != 1:
                            dialog.notification(xbmc.getLocalizedString(31715), xbmc.getLocalizedString(31719), xbmcgui.NOTIFICATION_ERROR, 5000)
                    else:
                        if wifi.State != 1:
                            dialog.notification(xbmc.getLocalizedString(31715), xbmc.getLocalizedString(31716), xbmcgui.NOTIFICATION_ERROR, 5000)
            self.FillList()
        pass

    def RefreshWifiState(self, labelControl):
        wifis = AlphaUINetworkUtils.WiFis()

        for wifi in wifis:
            if wifi.UUID == self.activeUuid:
                if wifi.State == 1 or wifi.State == 4:
                    return True
                else:
                    labelControl.setLabel(xbmc.getLocalizedString(31729) + xbmc.getLocalizedString((31721 + wifi.State)))
        return False