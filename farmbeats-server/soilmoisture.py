from grove import adc

class SoilMoistureSensor:
    def __init__(self, pin:int):
        self.__pin = pin
        self.__adc = adc.ADC()

    @property
    def moisture(self) -> int:
        return self.__adc.read(self.__pin)