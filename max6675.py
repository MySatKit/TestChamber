import spidev


bus = 0  # RPI 4 has only 1 bus with number 0
device = 0  # max6675 starts transmit on CS = 0

spi = spidev.SpiDev()
spi.open(bus, device)
spi.max_speed_hz = 500000
spi.mode = 0


def read_celsius():
    data = spi.readbytes(2)
    data >>= 3
    data *= 0.25
    return data
