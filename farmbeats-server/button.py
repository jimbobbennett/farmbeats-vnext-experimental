from grove.factory import Factory

class DualButton:
    def __init__(self, pin: int):
        self.__button1 = Factory.getButton("GPIO-LOW", pin)
        self.__button2 = Factory.getButton("GPIO-LOW", pin + 1)

        self.__button1_pressed = False
        self.__button2_pressed = False
    
    def capture_values(self) -> None:
        self.__button1_pressed = self.__button1.is_pressed()
        self.__button2_pressed = self.__button2.is_pressed()

    @property
    def button1(self) -> bool:
        return self.__button1_pressed

    @property
    def button2(self) -> bool:
        return self.__button2_pressed

