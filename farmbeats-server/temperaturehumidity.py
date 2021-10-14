from seeed_dht import DHT
from seeed_ds18b20 import grove_ds18b20

class TemperatureAndHumiditySensor:
    def __init__(self, dht_pin: int, soil_pin: int):
        self.__dht = DHT('11', dht_pin)
        self.__ds18b20 = grove_ds18b20()
        self.__soil_temperature = -1.0
        self.__temperature = -1
        self.__humidity = -1

    def capture_values(self) -> None:
        self.__soil_temperature, _ = self.__ds18b20.read_temp
        self.__humidity, self.__temperature = self.__dht.read()
    
    @property
    def soil_temperature(self) -> float:
        return self.__soil_temperature
    
    @property
    def temperature(self) -> int:
        return self.__temperature
    
    @property
    def humidity(self) -> int:
        return self.__humidity
