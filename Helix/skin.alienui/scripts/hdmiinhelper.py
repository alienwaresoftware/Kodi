import AlphaUIUtils

class HDMIInHelper(object):
    def __init__(self):
        pass

    def checkCableConnection(self):
        return AlphaUIUtils.IsHDMICableConnected()
        
    def enableHDMIIn(self):
        AlphaUIUtils.ToggleHDMISource()
        pass        
       

