import lgpio as scb

from typing import Union


class MyGPIO:

    forbidden_pins = {
        "sda": 2,
        "scl": 3,
        "tx": 14,
        "rx": 15,
        "mosi": 10,
        "miso": 9,
        "sclk": 11,
        "CE0": 8,
        "CE1": 7
    }

    def __init__(self) -> None:
        self.h = scb.gpiochip_open(0)
        if not self.h:
            return

    def __del__(self):
        scb.gpiochip_close(self.h)

    # ------------- Low-level API -------------
    def _set_direction(self, pin: int, *, output: bool):
        if pin not in self.forbidden_pins.values():
            if output:
                scb.gpio_claim_output(self.h, pin)
            else:
                scb.gpio_claim_input(self.h, pin)

    def _set_state(self, pin: int, state: bool):
        if pin not in self.forbidden_pins.values():
            if not isinstance(state, (bool, )):
                state = bool(state)
            scb.gpio_write(self.h, pin, int(state))

    def _get_pin_state(self, pin: int) -> int:
        if pin not in self.forbidden_pins.values():
            self._set_direction(pin, output=False)
            return scb.gpio_read(self.h, pin)
        else:
            return -1
    # ------------------------------------------


class MyRelay(MyGPIO):

    pins = {
        "liquid_nitrogen_relay": 23
    }

    def list_relays(self):
        return list(self.pins.keys())

    def add_relay(self, name: str, pin: int) -> int:
        """
        returns:
            -1 if pin is already in use
            -2 is name is already in use
            -3 if interface pin was provided

            0 if everythins is OK
        """
        if pin not in self.forbidden_pins.values():
            if pin in self.pins.values():
                return -1
            elif name in self.pins.keys():
                return -2
            else:
                self.pins[name] = pin
                return 0
        else:
            return -3

    def output_high(self, pin: Union[int, str]):
        if isinstance(pin, (str, )):
            temp = self.pins.get(pin)
            if temp is None:
                return
            pin = temp

        self._set_direction(pin, output=True)
        self._set_state(pin, True)

    def output_low(self, pin: Union[int, str]):
        if isinstance(pin, (str, )):
            temp = self.pins.get(pin)
            if temp is None:
                return
            pin = temp

        self._set_direction(pin, output=True)
        self._set_state(pin, False)

    def get_pin_state(self, pin) -> int:
        """
        returns:
            -1 if pin was provided by name and was not found
            0 or 1 if everything is OK

        raises 'Forbidden pin' if bus pin was used
        """
        if isinstance(pin, (str, )):
            temp = self.pins.get(pin)
            if temp is None:
                return -1
            pin = temp
        
        state = self._get_pin_state(pin)
        assert state != -1, "Forbidden pin"
        return state


if __name__ == "__main__":
    import time

    test = MyGPIO()
    test._set_direction(23, output=True)
    for i in range(5):
        test._set_state(23, True)
        time.sleep(1)
        test._set_state(23, False)
        time.sleep(1)
