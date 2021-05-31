from spidev import SpiDev


def read_celsius(bus: SpiDev):
    data = bus.readbytes(2)
    if data & 0x4:
        # no thermocouple attached!
        return -4096

    data >>= 3
    data *= 0.25
    return data


if __name__ == '__main__':
    bus_num = 0  # RPI 4 has only 1 bus_num with number 0
    device = 0  # max6675 starts transmit on CS = 0

    spi = SpiDev()
    spi.open(bus_num, device)
    spi.max_speed_hz = 500000
    spi.mode = 0

    read_celsius(spi)
