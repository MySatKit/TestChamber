#!/usr/bin/python

import time
from smbus2 import SMBus


MS5611_ADDRESS = 0x77


class MS5611:

    # commands
    RESET = 0x1E
    
    CONVERT_D1_256 = 0x40
    CONVERT_D1_512 = 0x42
    CONVERT_D1_1024 = 0x44
    CONVERT_D1_2048 = 0x46
    CONVERT_D1_4096 = 0x48

    CONVERT_D2_256 = 0x50
    CONVERT_D2_512 = 0x52
    CONVERT_D2_1024 = 0x54
    CONVERT_D2_2048 = 0x56
    CONVERT_D2_4096 = 0x58

    ADC_READ = 0x00

    def __init__(self, bus: SMBus) -> None:
        self.bus: SMBus = bus

        # Read 12 bytes of calibration data
        # Read pressure sensitivity
        try:
            data = bus.read_i2c_block_data(0x77, 0xA2, 2)
        except Exception:
            raise Exception("No MS5611 sensor on bus")
        self.C1 = data[0] * 256 + data[1]

        # Read pressure offset
        data = bus.read_i2c_block_data(0x77, 0xA4, 2)
        self.C2 = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure sensitivity
        data = bus.read_i2c_block_data(0x77, 0xA6, 2)
        self.C3 = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure offset
        data = bus.read_i2c_block_data(0x77, 0xA8, 2)
        self.C4 = data[0] * 256 + data[1]

        # Read reference temperature
        data = bus.read_i2c_block_data(0x77, 0xAA, 2)
        self.C5 = data[0] * 256 + data[1]

        # Read temperature coefficient of the temperature
        data = bus.read_i2c_block_data(0x77, 0xAC, 2)
        self.C6 = data[0] * 256 + data[1]

    def reset(self) -> None:
        self.bus.write_byte(MS5611_ADDRESS, self.RESET)

    def read_all(self) -> tuple:
        # MS5611_01BXXX address, 0x77(118)
        #		0x40(64)	Pressure conversion(OSR = 256) command
        self.bus.write_byte(0x77, self.CONVERT_D1_256)
        time.sleep(2.1 / 1000)  # sleep 2.1 ms

        # Read digital pressure value
        # Read data back from 0x00(0), 3 bytes
        # D1 MSB2, D1 MSB1, D1 LSB
        value = self.bus.read_i2c_block_data(0x77, 0x00, 3)
        D1 = value[0] * 65536 + value[1] * 256 + value[2]

        # MS5611_01BXXX address, 0x76(118)
        #		0x50(64)	Temperature conversion(OSR = 256) command
        self.bus.write_byte(0x77, self.CONVERT_D2_256)

        time.sleep(2.1 / 1000)

        # Read digital temperature value
        # Read data back from 0x00(0), 3 bytes
        # D2 MSB2, D2 MSB1, D2 LSB
        value = self.bus.read_i2c_block_data(0x77, 0x00, 3)
        D2 = value[0] * 65536 + value[1] * 256 + value[2]

        dT = D2 - self.C5 * 256
        TEMP = 2000 + dT * self.C6 / 8388608
        OFF = self.C2 * 65536 + (self.C4 * dT) / 128
        SENS = self.C1 * 32768 + (self.C3 * dT) / 256
        T2 = 0
        OFF2 = 0
        SENS2 = 0

        if TEMP >= 2000:
            T2 = 0
            OFF2 = 0
            SENS2 = 0
        elif TEMP < 2000:
            T2 = (dT * dT) / 2147483648
            OFF2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 2
            SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 4
            if TEMP < -1500:
                OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
                SENS2 = SENS2 + 11 * ((TEMP + 1500) * (TEMP + 1500)) / 2

        TEMP = TEMP - T2
        OFF = OFF - OFF2
        SENS = SENS - SENS2
        pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
        cTemp = TEMP / 100.0

        return pressure, cTemp


if __name__ == "__main__":
    _bus = SMBus(1)
    sensor = MS5611(_bus)
    pressure, temp = sensor.read_all()

    print(f"Temperature : {temp} C")
    print(f"Pressure    : {round(pressure, 3)} hPa")
