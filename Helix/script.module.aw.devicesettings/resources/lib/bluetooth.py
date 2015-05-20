import xbmc
import xbmcgui
import sys
import thread
from threading import Timer
import AlphaUIUtils

from waitdialog import WaitDialogHelper

class BluetoothDevice(object):
    def __init__(self, wifinetwork, uuid):
        pass

class BluetoothHelper(object):
    def __init__(self, bluetoothlistcontrol, addon, language):
        self.IsInitDone = False
        self._isBluetoothOn = True
        self.bluetooth = AlphaUIUtils.Bluetooth()
        self.bluetoothlistcontrol = bluetoothlistcontrol
        self.bluetoothDevices = None
        self.language = language
        self.addon = addon

        self.lock = thread.allocate_lock()
        self.IsInitDone = True

        self.discovertimer = Timer(1.0, self.discoverTimerFunc)
        self.discovertimer.start()
        
    def discoverTimerFunc(self):
        try:
            if self.IsInitDone:
                #print ("discovering")
                if (self._isBluetoothOn):
                    tempBluetoothDevices = self.bluetooth.Discover()
                    self.lock.acquire()
                    try:
                        self.bluetoothDevices = tempBluetoothDevices
                    finally:
                        self.lock.release()


                    self.lock.acquire()
                    try:                     
                        if (self.bluetoothlistcontrol.size() == 0):
                            for device in self.bluetoothDevices:
                                #print "Device Discovered {0} -> {1} -> {2} -> {3}".format(device.Name,device.Address,device.Authenticated,device.Connected)                                
                                if (device.Name != ""):
                                    li = xbmcgui.ListItem(device.Name,self.getDeviceState(device),"")
                                    li.setProperty('Paired',str(device.Authenticated and not device.Connected))            
                                    li.setProperty('NotPaired',str(not device.Authenticated))            
                                    li.setProperty('Connected',str(device.Connected))
                                    li.setProperty('Address',str(device.Address))
                                    li.setProperty('MarkDelete','0')

                                    self.bluetoothlistcontrol.addItem(li)
                        else:
                            for itemIndex in range(0,self.bluetoothlistcontrol.size()):
                                li = self.bluetoothlistcontrol.getListItem(itemIndex)                                
                                li.setProperty('MarkDelete','1')

                            for device in self.bluetoothDevices:
                                #print "Device Discovered {0} -> {1} -> {2} -> {3}".format(device.Name,device.Address,device.Authenticated,device.Connected)                                
                                isDeviceAdded = False
                                for itemIndex in range(0,self.bluetoothlistcontrol.size()):
                                    li = self.bluetoothlistcontrol.getListItem(itemIndex)
                                    if (device.Address == li.getProperty('Address')):
                                        isDeviceAdded = True
                                        li.setLabel(device.Name)
                                        li.setLabel2(self.getDeviceState(device))
                                        li.setProperty('Paired',str(device.Authenticated and not device.Connected))  
                                        li.setProperty('NotPaired',str(not device.Authenticated))            
                                        li.setProperty('Connected',str(device.Connected))
                                        li.setProperty('MarkDelete','0')
                                        break
                                    else:
                                        continue

                                if (not isDeviceAdded):
                                    if (device.Name != ""):
                                        li = xbmcgui.ListItem(device.Name,self.getDeviceState(device),"")
                                        li.setProperty('Paired',str(device.Authenticated and not device.Connected))  
                                        li.setProperty('NotPaired',str(not device.Authenticated))            
                                        li.setProperty('Connected',str(device.Connected))
                                        li.setProperty('Address',str(device.Address))
                                        li.setProperty('MarkDelete','0')

                                        self.bluetoothlistcontrol.addItem(li)

                            isItemRemoved = True
                            while(isItemRemoved):
                                isItemRemoved = False
                                for itemIndex in range(0,self.bluetoothlistcontrol.size()):
                                    li = self.bluetoothlistcontrol.getListItem(itemIndex)                                
                                    if (li.getProperty('MarkDelete') == '1'):
                                        self.bluetoothlistcontrol.removeItem(itemIndex)
                                        isItemRemoved = True
                                        break
                    finally:
                        self.lock.release()

                monitor = xbmc.Monitor()
                if monitor.waitForAbort(1):
                    return
                self.discovertimer = Timer(1.0, self.discoverTimerFunc)
                self.discovertimer.start()
        except:
            print("closing discoverTimerFunc")

    def isBluetoothOn(self):
        return self._isBluetoothOn

    def getDeviceState(self,device):        
        if (device.Connected):
            return self.language(33043)
        elif(device.Authenticated):
            return self.language(33044)
        else:
            return ''

    def callbackStatus(self,deviceName, statusId):
        #xbmcgui.Dialog().notification("callbackStatus", str(statusId) , xbmcgui.NOTIFICATION_INFO, 3000)
        if (statusId == 1):
            self.waitDialog.setLabel(self.language(33056).format(deviceName))
        elif (statusId == 2):
            self.waitDialog.setLabel(self.language(33057).format(deviceName))
        else:
            self.waitDialog.setLabel(self.language(33055).format(deviceName))

    def callbackYesNo(self,deviceName, displayNumber):
        return (xbmcgui.Dialog().yesno(self.language(33049), self.language(33050).format(deviceName),'',str(displayNumber)) == 1)

    def callbackUnknown(self,deviceName,ioCapability,authenticationMethod,numericValue,passkey):
        print 'callbackUnknown'
        print ioCapability
        print authenticationMethod
        print numericValue
        print passkey

    def findDeviceFromAddress(self, address):
        selectedDevice = None
        self.lock.acquire()
        try:
            for device in self.bluetoothDevices:
                if (device.Address == address):
                    selectedDevice = device
        finally:
            self.lock.release()

        return selectedDevice

    def authenticateOrRemoveDevice(self, address):
        selectedDevice = self.findDeviceFromAddress(address)

        if (selectedDevice == None):
            xbmcgui.Dialog().notification(self.language(33018), self.language(33047), xbmcgui.NOTIFICATION_ERROR, 15000)
        else:
            self.lock.acquire()
            try:
                if (selectedDevice.Authenticated):
                    if (xbmcgui.Dialog().yesno(self.language(33051), self.language(33052).format(selectedDevice.Name)) == 1):
                        if(selectedDevice.RemoveDevice()):
                            xbmcgui.Dialog().notification(self.language(33020), self.language(33054).format(selectedDevice.Name), xbmcgui.NOTIFICATION_INFO, 15000)
                            self.bluetoothDevices = []
                        else:
                            xbmcgui.Dialog().notification(self.language(33018),self.language(33053).format(selectedDevice.Name), xbmcgui.NOTIFICATION_ERROR, 15000)             
                else:
                    self.waitDialog = WaitDialogHelper().create()
                    if (selectedDevice.Authenticate(self.callbackStatus, self.callbackYesNo,self.callbackUnknown)):
                        xbmcgui.Dialog().notification(self.language(33020), self.language(33048), xbmcgui.NOTIFICATION_INFO, 15000)
                        self.bluetoothDevices = []
                    else:
                        xbmcgui.Dialog().notification(self.language(33018),self.language(33047), xbmcgui.NOTIFICATION_ERROR, 15000)
                    self.waitDialog.close()
            finally:
                self.lock.release()

    def close(self):
        self.IsInitDone = False
