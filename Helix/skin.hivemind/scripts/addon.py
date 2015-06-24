import os, sys
import xbmcgui
from alienfx import *

ALIENFX_LIST_CONTROL = 9081

ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
ALIGN_CENTER = 6
MAX_NUMBER_OF_COLORS = 20

CONTROL_SIZE = 16
CONTROL_SELECTED_SIZE = 24

_imagePath = 'special://skin/media/alienware/alienfx/{0}'
_imageAlienheadPath = 'special://skin/media/alienware/alienfx/alien.png'
_imageCornerPath = 'special://skin/media/alienware/alienfx/corner.png'
_imageBrightnessPath = 'special://skin/media/alienware/alienfx/brightness.png'
_imageSelectedPath = 'special://skin/media/alienware/alienfx/selected.png'
_imageBlackPath = 'special://skin/media/alienware/alienfx/blank.png'

class AlienFXLights(object):

    def __init__(self, win):
        self.colors = [0xFF0000F0, 0xFF0060F0, 0xFF00A0F0, 0xFF00F0F0, 0xFF46F091, 0xFF00F055, 0xFF00F000, 0xFF64F523, 0xFFA0F000, 0xFFD0F000, 
           0xFFF0E000, 0xFFF08000, 0xFFF05000, 0xFFF00000, 0xFFF00070, 0xFFF000B0, 0xFFF000F0, 0xFF9000F0, 0xFF6400F0, 0xFF000000]
        self.maximumBrightness = 100
        self.minimumBrightness = 30
        self.currentBrightness = 30
        self.brightnessSpinIndex = 0
        self.zone1SelectedColor = 0xFF0000F0
        self.zone2SelectedColor = 0xFF0000F0
        self._win = win        
        self.__createControls()
        self.__initController()

    def __createControls(self):
      
        self.__zone1Buttons = []
        self.__zone2Buttons = []

        startingX = 700
        startingY = 171

        visibilityCondition = '[Container(9000).Position(2)] + [Control.HasFocus(9081) | ControlGroup(9082).HasFocus()]'

        imageHead = xbmcgui.ControlImage(-100, 100, 28, 33, _imageAlienheadPath)
        self._win.addControl(imageHead)
        imageHead.setVisibleCondition(visibilityCondition,False)
        imageHead.setPosition(startingX - 70, startingY)

        imageCorner = xbmcgui.ControlImage(-100, 100, 35, 31, _imageCornerPath)
        self._win.addControl(imageCorner)
        imageCorner.setVisibleCondition(visibilityCondition,False)
        imageCorner.setPosition(startingX - 72, startingY + 47)

        imageBrightness = xbmcgui.ControlImage(-100, 100, 35, 35, _imageBrightnessPath)
        self._win.addControl(imageBrightness)
        imageBrightness.setVisibleCondition(visibilityCondition,False)
        imageBrightness.setPosition(startingX - 71, startingY + 90)

        # zones controls
        index = 0
        for color in self.colors:
            fileName = hex(color).replace('0x', '').upper().replace('L', '') + '.png'
            filePath = _imagePath.format(fileName)
            zoneButtonX = startingX + (index * CONTROL_SIZE)
            zone1ButtonY = startingY + 9
            zone1Button = xbmcgui.ControlImage(-100, -100 , CONTROL_SIZE, CONTROL_SIZE, filePath, aspectRatio=2)            
            zone1Button.setVisible(False)
            self.__zone1Buttons.append(zone1Button)
            self._win.addControl(self.__zone1Buttons[-1])
            zone1Button.setVisibleCondition(visibilityCondition,False)
            zone1Button.setPosition(zoneButtonX,zone1ButtonY)

            zone2ButtonY = startingY + 53
            zone2Button = xbmcgui.ControlImage(-100, -100 , CONTROL_SIZE, CONTROL_SIZE, filePath, aspectRatio=2)
            zone2Button.setVisible(False)
            self.__zone2Buttons.append(zone2Button)
            self._win.addControl(self.__zone2Buttons[-1])
            zone2Button.setVisibleCondition(visibilityCondition,False)
            zone2Button.setPosition(zoneButtonX,zone2ButtonY)

            index += 1

    def __setButtonHighlight(self, zoneId, selectedIndex):
        if (zoneId == 1):
            zoneButton = self.__zone1Buttons;
        else:
            zoneButton = self.__zone2Buttons;

        selectedFileName = hex(self.colors[selectedIndex]).replace('0x', '').upper().replace('L', '') + 's.png'
        selectedFilePath = _imagePath.format(selectedFileName)

        zoneButton[selectedIndex].setImage(selectedFilePath);
        zoneButton[selectedIndex].setWidth(CONTROL_SELECTED_SIZE);
        zoneButton[selectedIndex].setHeight(CONTROL_SELECTED_SIZE);
        x = zoneButton[selectedIndex].getX();
        y = zoneButton[selectedIndex].getY() - (CONTROL_SELECTED_SIZE - CONTROL_SIZE)/2;

        zoneButton[selectedIndex].setPosition(x,y);

        for i in range(selectedIndex+1, MAX_NUMBER_OF_COLORS):
            x = zoneButton[i].getX() + (CONTROL_SELECTED_SIZE - CONTROL_SIZE);
            y = zoneButton[i].getY();
            zoneButton[i].setPosition(x,y);

    def __adjustButtonHighlight(self, zoneId, previousIndex, selectedIndex):
        if (zoneId == 1):
            zoneButton = self.__zone1Buttons;
        else:
            zoneButton = self.__zone2Buttons;

        selectedFileName = hex(self.colors[selectedIndex]).replace('0x', '').upper().replace('L', '') + 's.png'
        selectedFilePath = _imagePath.format(selectedFileName)

        normalFileName = hex(self.colors[previousIndex]).replace('0x', '').upper().replace('L', '') + '.png'
        normalFilePath = _imagePath.format(normalFileName)


        if (selectedIndex > previousIndex):
            zoneButton[previousIndex].setImage(normalFilePath);
            zoneButton[previousIndex].setWidth(CONTROL_SIZE);
            zoneButton[previousIndex].setHeight(CONTROL_SIZE);
            x = zoneButton[previousIndex].getX();
            y = zoneButton[previousIndex].getY() + (CONTROL_SELECTED_SIZE - CONTROL_SIZE)/2;

            zoneButton[previousIndex].setPosition(x,y);

            zoneButton[selectedIndex].setImage(selectedFilePath);
            zoneButton[selectedIndex].setWidth(CONTROL_SELECTED_SIZE);
            zoneButton[selectedIndex].setHeight(CONTROL_SELECTED_SIZE);
            x = zoneButton[selectedIndex].getX() - (CONTROL_SELECTED_SIZE - CONTROL_SIZE);
            y = zoneButton[selectedIndex].getY() - (CONTROL_SELECTED_SIZE - CONTROL_SIZE)/2;

            zoneButton[selectedIndex].setPosition(x,y);
        else:
            zoneButton[selectedIndex].setImage(selectedFilePath);
            zoneButton[selectedIndex].setWidth(CONTROL_SELECTED_SIZE);
            zoneButton[selectedIndex].setHeight(CONTROL_SELECTED_SIZE);
            x = zoneButton[selectedIndex].getX();
            y = zoneButton[selectedIndex].getY() - (CONTROL_SELECTED_SIZE - CONTROL_SIZE)/2;

            zoneButton[selectedIndex].setPosition(x,y);

            zoneButton[previousIndex].setImage(normalFilePath);
            zoneButton[previousIndex].setWidth(CONTROL_SIZE);
            zoneButton[previousIndex].setHeight(CONTROL_SIZE);
            x = zoneButton[previousIndex].getX() + (CONTROL_SELECTED_SIZE - CONTROL_SIZE);
            y = zoneButton[previousIndex].getY() + (CONTROL_SELECTED_SIZE - CONTROL_SIZE)/2;

            zoneButton[previousIndex].setPosition(x,y);

    def __initializeControls(self, isSetFocus):
        #print "__initializeControls with isSetFocus = {0}".format(isSetFocus)
        try:
            brightnessResult = self.__ctrl.GetBrightnessData()
            if brightnessResult.count > 0:
                #print brightnessResult
                self.minimumBrightness = brightnessResult[0]
                self.maximumBrightness = brightnessResult[1]
                self.currentBrightness = brightnessResult[-1]

                self.brightnessSpinIndex = int(round(float(self.currentBrightness - self.minimumBrightness) * (100 / float(self.maximumBrightness - self.minimumBrightness))))

            zoneResult = self.__ctrl.GetCurrentColors()
            #print "zoneResult -> {0},{1}".format(zoneResult[0].Color, zoneResult[1].Color)
            if zoneResult.count > 0:
                if zoneResult[0].Color in self.colors:
                    index = self.colors.index(zoneResult[0].Color)
                    self.zone1SelectedColor = zoneResult[0].Color
                    self.__setButtonHighlight(1,index)
                    #print "zone 1 color {0}, index {1}".format(zoneResult[0].Color,index)

                if zoneResult[1].Color in self.colors:
                    index = self.colors.index(zoneResult[1].Color)
                    self.zone2SelectedColor = zoneResult[1].Color
                    self.__setButtonHighlight(2,index)
                    #print "zone 2 color {0}, index {1}".format(zoneResult[1].Color,index)
        except:
            print "addon.py::__initializeControls:", sys.exc_info()[0]
            pass

    def __initController(self):
        try:
            self.__ctrl = AlienFXController()
            self.__ctrl.Initialize()
            self.__initializeControls(False)        
        except:
            print "addon.py::__initController:", sys.exc_info()[0]
            pass

    def setFocus(self):
        self.__initializeControls(True)

    def release(self):
        try:
            self.__ctrl.Release()
        except:
            print "addon.py::release:", sys.exc_info()[0]
            pass

    def setBrightness(self, brightness):
        try:
            pct = int(round(brightness * float(float(self.maximumBrightness - self.minimumBrightness) /self.maximumBrightness))) + self.minimumBrightness
            self.__ctrl.SetBrightness(pct)
            self.brightnessSpinIndex = brightness
        except:
            print "addon.py::setBrightness:", sys.exc_info()[0]
            pass

    def setColor(self, zoneId, selectedIndex):
        try:
            if zoneId > 0:
                self.__ctrl.SetColor(zoneId, self.colors[selectedIndex])
                self.__ctrl.Update()

            if (zoneId == 1):
                previousIndex = self.colors.index(self.zone1SelectedColor)
                self.zone1SelectedColor = self.colors[selectedIndex]
            else:
                previousIndex = self.colors.index(self.zone2SelectedColor)
                self.zone2SelectedColor = self.colors[selectedIndex]

            self.__adjustButtonHighlight(zoneId,previousIndex,selectedIndex);

        except:
            print "addon.py::setColor:", sys.exc_info()[0]
            pass