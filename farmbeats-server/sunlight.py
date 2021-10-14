from seeed_si114x import grove_si114x

class SunLightSensor:
    def __init__(self):
        self.__si114x = grove_si114x()
        self.__visible = -1
        self.__infra_red = -1
        self.__ultra_violet = -1

    def capture_values(self) -> None:
        self.__visible = self.__si114x.ReadVisible
        self.__infra_red = self.__si114x.ReadIR
        self.__ultra_violet = self.__si114x.ReadUV/100
    
    @property
    def visible(self) -> int:
        return self.__visible
    
    @property
    def infra_red(self) -> int:
        return self.__infra_red
    
    @property
    def ultra_violet(self) -> float:
        return self.__ultra_violet