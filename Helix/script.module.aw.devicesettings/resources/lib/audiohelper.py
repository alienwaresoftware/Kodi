import AlphaUIUtils
import sys

class AudioHelper(object):
    def __init__(self):
        try:
            self.audio = AlphaUIUtils.GetAudio()
            self.outputs = self.audio.GetOutputs()        
        except:
            print "audiohelper.py::__init__:", sys.exc_info()[0]
        pass

    def getOutputs(self):
        outputs = []
        try:
            for output in self.outputs:
                outputs.append(output.Name)
            #print outputs
        except:
            print "audiohelper.py::getOutputs:", sys.exc_info()[0]
        return outputs

    def setOutput(self, selectedIndex):
        #print(selectedIndex)
        #print(self.outputs[selectedIndex].Name)
        try:
            return self.outputs[selectedIndex].SetDefault()            
        except:
            print "audiohelper.py::setOutput:", sys.exc_info()[0]
            return False;

    def getVolume(self):
        try:
            return self.audio.GetVolume()
        except:
            print "audiohelper.py::getVolume:", sys.exc_info()[0]
        return 0

    def setVolume(self, volume):
        try:
            self.audio.SetVolume(volume)
        except:
            print "audiohelper.py::setVolume:", sys.exc_info()[0]
    
    def getSelectedOutput(self):       
        try:
            for output in self.outputs:
                if output.IsDefault:
                    return output.Name
        except:
            print "audiohelper.py::getSelectedOutput:", sys.exc_info()[0]
        return "HDMI"
    
    def getOutputNameFromIndex(self,selectedIndex):       
        try:
            index = 0
            for output in self.outputs:
                if (index == selectedIndex):
                    return output.Name
                index += 1
        except:
            print "audiohelper.py::getOutputNameFromIndex:", sys.exc_info()[0]
        return "HDMI"
    
    def getSelectedIndex(self):       
        try:
            i = 0
            for output in self.outputs:
                if output.IsDefault:
                    return i
                i += 1
        except:
            print "audiohelper.py::getSelectedIndex:", sys.exc_info()[0]
        return 0
    
    def getSpeakerConfigs(self, selectedIndex):       
        speakerConfigList = []
        try:
            speakerConfigs = self.outputs[selectedIndex].GetSpeakerConfigs()
            for config in speakerConfigs:
                speakerConfigList.append(config.Name)
        except:
            print "audiohelper.py::getSpeakerConfigs:", sys.exc_info()[0]
        return speakerConfigList
    
    def getSelectedSpeakerConfig(self, selectedIndex):       
        try:
            speakerConfigs = self.outputs[selectedIndex].GetSpeakerConfigs()
            for config in speakerConfigs:
                if config.IsDefault:
                    return config.Name
        except:
            print "audiohelper.py::getSelectedSpeakerConfig:", sys.exc_info()[0]
        return None
        
    def setSpeakerConfig(self, audioSelectedIndex, selectedIndex):
        #print(selectedIndex)
        #print(self.outputs[selectedIndex].Name)
        try:
            speakerConfigs = self.outputs[audioSelectedIndex].GetSpeakerConfigs()
            for config in speakerConfigs:
                if (config.Index == selectedIndex):
                    return config.SetDefault()
        except:
            print "audiohelper.py::setSpeakerConfig:", sys.exc_info()[0]
        return False

    def isMute(self):
        try:
            return (self.audio.GetMute() == 1)
        except:
            print "audiohelper.py::isMute:", sys.exc_info()[0]
        return False

    def setMute(self, mute):
        try:
            if (mute):
                self.audio.SetMute(1)
            else:
                self.audio.SetMute(0)
        except:
            print "audiohelper.py::setMute:", sys.exc_info()[0]
