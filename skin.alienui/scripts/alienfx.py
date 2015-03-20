import ctypes
from ctypes import *

class ALIENFX_UI_ZONE_DATA(Structure):
    _fields_ = [("ZoneID", c_uint32),
                ("Color", c_uint32)]

class AlienFXController:    
    def __init__(self):
        self.__AlienFXDLL = CDLL('AlienFXUI.dll')
        # AlienFXUI_Initialize
        self.__initFunction = self.__AlienFXDLL.AlienFXUI_Initialize
        self.__initFunction.restype = c_uint32
        self.__initFunction.argtypes = [c_char_p]
        # AlienFXUI_Relase
        self.__releaseFunction = self.__AlienFXDLL.AlienFXUI_Release
        self.__releaseFunction.restype = c_uint32
        # AlienFXUI_GetZonesData
        self.__getZonesDataFunction = self.__AlienFXDLL.AlienFXUI_GetZonesData
        self.__getZonesDataFunction.restype = c_uint32
        self.__getZonesDataFunction.argtypes = [c_uint32, POINTER(POINTER(ALIENFX_UI_ZONE_DATA)), POINTER(c_int32)]

        # AlienFXUI_GetBrightnessData
        self.__getBrightnessDataFunction = self.__AlienFXDLL.AlienFXUI_GetBrightnessData
        self.__getBrightnessDataFunction.restype = c_uint32
        self.__getBrightnessDataFunction.argtypes = [POINTER(c_int32), POINTER(c_int32), POINTER(c_int32)]

        # AlienFXUI_SetBrightness
        self.__setBrightnessFunction = self.__AlienFXDLL.AlienFXUI_SetBrightness
        self.__setBrightnessFunction.restype = c_uint32
        self.__setBrightnessFunction.argtypes = [c_int32]

        # AlienFXUI_SetColor
        self.__setColorFunction = self.__AlienFXDLL.AlienFXUI_SetColor
        self.__setColorFunction.restype = c_uint32
        self.__setColorFunction.argtypes = [c_int32, c_int32, c_int32]

        # AlienFXUI_Update
        self.__updateFunction = self.__AlienFXDLL.AlienFXUI_Update
        self.__updateFunction.restype = c_uint32

    def Initialize(self):
        userName = create_string_buffer(b'AlphaConsole')
        return self.__initFunction(userName)
    
    def Release(self):
        return self.__releaseFunction()

    def GetCurrentColors(self):
        numberOfZones = c_int32()
        zonesPtr = POINTER(ALIENFX_UI_ZONE_DATA)()
        result = self.__getZonesDataFunction(0, byref(zonesPtr), byref(numberOfZones))
        if numberOfZones.value > 0:
            zoneSize = ctypes.sizeof(ALIENFX_UI_ZONE_DATA)
            firstZone = self.__deref(zonesPtr, ALIENFX_UI_ZONE_DATA)
            secondZone = self.__deref(addressof(firstZone) + zoneSize, ALIENFX_UI_ZONE_DATA)
            return [firstZone, secondZone]
        return []

    def GetBrightnessData(self):
        minimumBrightness = c_int32()
        maximumBrightness = c_int32()
        currentBrightness = c_int32()
        result = self.__getBrightnessDataFunction(byref(minimumBrightness), byref(maximumBrightness), byref(currentBrightness))
        if result == 0:
            return [minimumBrightness.value, maximumBrightness.value, currentBrightness.value]
        return []

    def SetBrightness(self, brigthness):
        return self.__setBrightnessFunction(brigthness)

    def SetColor(self, zone, color):
        return self.__setColorFunction(0, zone, color)

    def Update(self):
        return self.__updateFunction()

    def __deref(self, addr, typ):
        return ctypes.cast(addr, ctypes.POINTER(typ)).contents        
