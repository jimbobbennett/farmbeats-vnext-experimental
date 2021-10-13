from grove.grove_relay import GroveRelay

class Relay:
    def __init__(self, relay_port: int):
        self.__relay = GroveRelay(relay_port)
    
    def on(self) -> None:
        self.__relay.on()

    def off(self) -> None:
        self.__relay.off()
    
    @property
    def state(self) -> bool:
        return self.__relay.read() == 1
