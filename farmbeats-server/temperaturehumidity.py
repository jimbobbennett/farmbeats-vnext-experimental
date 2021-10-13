from seeed_dht import DHT
from seeed_ds18b20 import grove_ds18b20

class TemperatureAndHumiditySensor:
    def __init__(self, dht_pin: int, soil_pin: int):
        self.__dht = DHT('11', dht_pin)
        self.__ds18b20 = grove_ds18b20()
    
    @property
    def soil_temperature(self) -> float:
        temp, _ = self.__ds18b20.read_temp
        return temp
    
    @property
    def temperature(self) -> int:
        _, temp = self.__dht.read()
        return temp
    
    @property
    def humidity(self) -> int:
        humidity, _ = self.__dht.read()
        return humidity
