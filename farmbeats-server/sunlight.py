from seeed_si114x import grove_si114x

class SunLightSensor:
    def __init__(self):
        self.__si114x = grove_si114x()
    
    @property
    def visible(self) -> int:
        return self.__si114x.ReadVisible
    
    @property
    def infra_red(self) -> int:
        return self.__si114x.ReadIR
    
    @property
    def ultra_voilet(self) -> float:
        return self.__si114x.ReadUV/100