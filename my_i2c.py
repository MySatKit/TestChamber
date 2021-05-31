from smbus2 import SMBus
from typing import Union
from os.path import exists


class MyI2CBus(SMBus):

    def __init__(self, bus: Union[None, int, str], slave_addr = None) -> None:
        """
        :param bus: i2c bus number (e.g. 0 or 1)
            or an absolute file path (e.g. `/dev/i2c-42`).
            If not given, a subsequent  call to ``open()`` is required.
        
        :param slave_addr: implement for usage as slave device
        """
        super().__init__(bus=bus)
        self.slave_addr = slave_addr
        self.bus = bus
        self.devices: dict = {}

    def __getitem__(self, item):
        return self.devices[item]

    def __setitem__(self, key, value):
        self.devices[key] = value

    def __delitem__(self, key):
        del self.devices[key]

    def load_devices(self, path: str):
        """
        uploads devices from config file

        format is:
        <name> <address with 16 base>
        ex.:
        bme280 0x60
        """
        if not exists(path):
            return

        with open(path) as handle:
            data = handle.readlines()
        
        if data:
            self.devices.clear()
        for row in data:
            name, addr = row.split()
            self.add_device(name, int(addr, base=16))

