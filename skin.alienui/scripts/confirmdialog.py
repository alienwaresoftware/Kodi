import xbmc
import xbmcgui
import os
import thread

from threading import Timer

ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

YES_NO_DIALOG = 0
CANCEL_RESTART_DIALOG = 1

class ConfirmDialogXML(xbmcgui.WindowXMLDialog):
    def onInit(self):
        self.IsInitDone = False
        self.labelControl = self.getControl(4110);
        self.yesNoDialog = self.getControl(4101);
        self.countDownLabelControl = self.getControl(4111);
        self.cancelRestartDialog = self.getControl(4104);
        self.okDialog = self.getControl(4107);
        self.clickid = -1

        self.labelControl.setLabel(self.__text);
        self.yesNoDialog.setVisible(False);
        self.cancelRestartDialog.setVisible(False);
        self.okDialog.setVisible(False);
        self.countDownLabelControl.setVisible(False);
        if self.__dialogType == ConfirmDialogType.yesNo:
            self.yesNoDialog.setVisible(True);
            self.setFocusId(4102);
        elif self.__dialogType == ConfirmDialogType.cancelRestart:
            self.cancelRestartDialog.setVisible(True);
            self.setFocusId(4105);
        elif self.__dialogType == ConfirmDialogType.ok:
            self.okDialog.setVisible(True);
            self.setFocusId(4108);

        if self.__timerValue > 0:
            self.countDown = self.__timerValue
            self.countDownLabelControl.setLabel(str(self.countDown))
            self.countDownLabelControl.setVisible(True);
            self.lock = thread.allocate_lock()
            self.countDownTimer = Timer(1.0, self.countDownTimerCallback)
            self.countDownTimer.start()

        self.IsInitDone = True

    def countDownTimerCallback(self):
        self.lock.acquire()
        try:
            if self.IsInitDone:
                if self.countDown > 0:
                    self.countDown = self.countDown - 1;
                    self.countDownLabelControl.setLabel(str(self.countDown))
                    #print self.__statusCallback
                    if self.__statusCallback is not None:
                        autoClose = self.__statusCallback(self.labelControl)
                        if autoClose:
                            self.clickid = 1
                            self.close()
                            return
                    self.countDownTimer = Timer(1.0, self.countDownTimerCallback)
                    self.countDownTimer.start()
                else:
                    self.clickid = 1
                    self.close()
        except:
            print("closing countDownTimer")
        finally: 
            #print("finally countDownTimer")
            self.lock.release()

    def onAction(self, action):
        #print "ACtion %s" % action.getId()
        if action == ACTION_SELECT_ITEM:
            self.buttonClickHandler(self.getFocusId())

    def onClick(self, controlID):
        #print controlID
        self.buttonClickHandler(controlID)

    def buttonClickHandler(self, controlId):
        if controlId == 4102 or controlId == 4105:
            self.clickid = 0
        elif controlId == 4103 or controlId == 4106:
            self.clickid = 1
        elif controlId == 4108:
            self.clickid = 1

        if self.__timerValue > 0:
            self.lock.acquire()

        self.IsInitDone = False
        
        if self.__timerValue > 0:
            self.lock.release()
            self.countDownTimer.cancel()
        self.close()                

    def setText(self, text):
        self.__text = text;

    def setDialogType(self, id):
        self.__dialogType = id

    def setTimer(self, timerValue):
        self.__timerValue = timerValue

    def setStatusCallback(self, statusCallback):
        self.__statusCallback = statusCallback

class ConfirmDialog(object):

    def doModal(self, text, dialogType, timerValue):
        mywin = ConfirmDialogXML("confirmdialog.xml",os.getcwd())
        mywin.setText(text)
        mywin.setDialogType(dialogType)
        mywin.setTimer(timerValue)
        mywin.setStatusCallback(None)
        mywin.doModal()
        clickid = mywin.clickid
        del mywin
        return clickid    
    
    def doModalWithCallback(self, text, dialogType, timerValue, statusCallback):
        mywin = ConfirmDialogXML("confirmdialog.xml",os.getcwd())
        mywin.setText(text)
        mywin.setDialogType(dialogType)
        mywin.setTimer(timerValue)
        mywin.setStatusCallback(statusCallback)
        mywin.doModal()
        clickid = mywin.clickid
        del mywin
        return clickid

class ConfirmDialogType(object):
    yesNo = 0
    cancelRestart = 1
    ok = 2
