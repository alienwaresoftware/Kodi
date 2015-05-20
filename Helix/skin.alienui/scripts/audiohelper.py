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
                outputs.append(output.Type)
            #print outputs
        except:
            print "audiohelper.py::getOutputs:", sys.exc_info()[0]
        return outputs

    def setOutput(self, selectedIndex):
        #print(selectedIndex)
        #print(self.outputs[selectedIndex].Name)
        try:
            self.outputs[selectedIndex].SetDefault()
            self.outputs = self.audio.GetOutputs()        
            return True;
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
                    return output.Type
        except:
            print "audiohelper.py::getSelectedOutput:", sys.exc_info()[0]
        return "HDMI"

