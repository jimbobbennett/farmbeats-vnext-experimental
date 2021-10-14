from grove import adc

class SoilMoistureSensor:
    def __init__(self, pin:int):
        self.__pin = pin
        self.__adc = adc.ADC()
        self.__moisture = -1

    def capture_values(self) -> None:
        self.__moisture = self.__adc.read(self.__pin)

    @property
    def moisture(self) -> int:
        return self.__moisture