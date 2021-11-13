import RPi.GPIO as GPIO

from abstraction import AbstractDriver


# using physical pin numbers
GPIO.setmode(GPIO.BOARD)


class RelayDriver(AbstractDriver):

    def __init__(self, pin_num: int):
        self.pin = pin_num
        if self.pin >= 0:
            GPIO.setup(self.pin, GPIO.OUTPUT)

    def update(self, state: bool) -> None:
        if self.pin >= 0:
            if state:
                GPIO.output(self.pin, GPIO.HIGH)
            else:
                GPIO.output(self.pin, GPIO.LOW)
