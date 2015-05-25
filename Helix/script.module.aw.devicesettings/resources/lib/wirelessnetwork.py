import xbmc
import xbmcgui
import sys
import AlphaUINetworkUtils

class WirelessNetwork(object):
    def __init__(self, wifinetwork, uuid):
        self.wifinetworkobj = wifinetwork
        self.ssid  = self.wifinetworkobj.SSID
        self.connected = self.wifinetworkobj.Connected
        self.securityenabled = self.wifinetworkobj.SecurityEnabled
        self.signal = self.wifinetworkobj.SignalQuality
        self.uuid = uuid

        if self.signal <= 20:
            self.signalimage = "alienware/wifi/wireless1.png"
        elif self.signal <= 40:
            self.signalimage = "alienware/wifi/wireless2.png"
        elif self.signal <= 60:
            self.signalimage = "alienware/wifi/wireless3.png"
        elif self.signal <= 80:
            self.signalimage = "alienware/wifi/wireless4.png"
        else:
            self.signalimage = "alienware/wifi/wireless5.png"

    def connect(self, passwd):
        self.wifinetworkobj.Connect(unicode(passwd))

    def connectNoPassword(self):
        self.wifinetworkobj.Connect()

    def disconnect(self):
        self.wifinetworkobj.Disconnect()


class WiFiHelper(object):
    def __init__(self, wifilistcontrol, language):
        self.wifilistcontrol = wifilistcontrol
        self.language = language

    def FillList(self):
        self.wifilistcontrol.reset()

        try:
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
        except:
            print "wirelessnetwork.py::WiFiHelper.FillList:", sys.exc_info()[0]

    def TakeAction(self, item):
        dialog = xbmcgui.Dialog()
        selectednetwork = self.allnetworks[int(item.getProperty('index'))]
        isaction = False
        isConnected = selectednetwork.connected
        self.activeUuid = selectednetwork.uuid

        if not selectednetwork.connected:            
            try:
                if selectednetwork.securityenabled:
                    passwd = dialog.input(self.language(33023).format(selectednetwork.ssid),type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
                    if passwd != "":
                        selectednetwork.connect(passwd)
                        isaction = True
                else:
                    selectednetwork.connectNoPassword()
                    isaction = True
            except:
                dialog.notification(self.language(33018), self.language(33025), xbmcgui.NOTIFICATION_ERROR, 15000)

        else:
            try:
                ret = dialog.yesno(self.language(33026), self.language(33027).format(selectednetwork.ssid))
                if ret:
                    selectednetwork.disconnect()
                    isaction = True
            except:
                dialog.notification(self.language(33018), self.language(33028), xbmcgui.NOTIFICATION_ERROR, 15000)

        if isaction:
            #confirmDialog = ConfirmDialog()
            if isConnected:
                dialogStr = self.language(33032)
            else:
                dialogStr = self.language(33036)

               
            dp = xbmcgui.DialogProgress()
            dp.create(self.language(33037),dialogStr)
            dp.update(0)

            progressCount = 0
            progressMaxCount = 20

            monitor = xbmc.Monitor()
            while not self.IsActiveWifiIdle(): 
                if dp.iscanceled():
                    dp.close()
                    break
                if monitor.waitForAbort(1):
                    # Abort was requested while waiting. We should exit
                    dp.close()
                    break
                progressCount = progressCount + 1
                if (progressCount >= progressMaxCount):
                    dp.close()
                    break               
                percent = int((float((float(progressCount) / float(progressMaxCount))) * float(100)))
                #print "Percent {0}, progressCount {1} ".format(percent, progressCount)
                dp.update(percent,self.language((33029 + self.GetActiveWifiState())))
              

            if isConnected:
                if self.GetActiveWifiState() != 4 and self.GetActiveWifiState() != 1:
                    dialog.notification(self.language(33018), self.language(33028), xbmcgui.NOTIFICATION_ERROR, 15000)
            else:
                if self.GetActiveWifiState() != 1:
                    dialog.notification(self.language(33018), self.language(33025), xbmcgui.NOTIFICATION_ERROR, 15000)

            self.FillList()

    def IsActiveWifiIdle(self):
        wifis = AlphaUINetworkUtils.WiFis()

        for wifi in wifis:
            if wifi.UUID == self.activeUuid:
                if wifi.State == 1 or wifi.State == 4:
                    return True
        return False

    def GetActiveWifiState(self):
        wifis = AlphaUINetworkUtils.WiFis()

        for wifi in wifis:
            if wifi.UUID == self.activeUuid:
                return wifi.State
        return 1
