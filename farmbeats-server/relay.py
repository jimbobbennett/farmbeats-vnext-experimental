from grove.grove_relay import GroveRelay

class Relay:
    def __init__(self, relay_port: int):
        self.__relay = GroveRelay(relay_port)
        self.__relay_state = False
    
    def on(self) -> None:
        self.__relay.on()

    def off(self) -> None:
        self.__relay.off()
    
    def capture_values(self) -> None:
        self.__relay_state = self.__relay.read() == 1
    
    @property
    def state(self) -> bool:
        return self.__relay_state
