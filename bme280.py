#!/usr/bin/python

import time
from smbus2 import SMBus

from my_utils import *

BME280_ADDRESS = 0x76  # Default device I2C address


class BME280:
    # Register Addresses
    BME280_REGISTER_DIG_T1 = 0x88
    BME280_REGISTER_DIG_T2 = 0x8A
    BME280_REGISTER_DIG_T3 = 0x8C

    BME280_REGISTER_DIG_P1 = 0x8E
    BME280_REGISTER_DIG_P2 = 0x90
    BME280_REGISTER_DIG_P3 = 0x92
    BME280_REGISTER_DIG_P4 = 0x94
    BME280_REGISTER_DIG_P5 = 0x96
    BME280_REGISTER_DIG_P6 = 0x98
    BME280_REGISTER_DIG_P7 = 0x9A
    BME280_REGISTER_DIG_P8 = 0x9C
    BME280_REGISTER_DIG_P9 = 0x9E

    BME280_REGISTER_DIG_H1 = 0xA1
    BME280_REGISTER_DIG_H2 = 0xE1
    BME280_REGISTER_DIG_H3 = 0xE3
    BME280_REGISTER_DIG_H4 = 0xE4
    BME280_REGISTER_DIG_H5 = 0xE5
    BME280_REGISTER_DIG_H6 = 0xE7

    BME280_REGISTER_CHIP_ID = 0xD0
    BME280_REGISTER_VERSION = 0xD1
    BME280_REGISTER_SOFT_RESET = 0xE0

    BME280_REGISTER_CAL26 = 0xE1  # R calibration stored in 0xE1 - 0xF0

    BME280_REGISTER_CONTROL_HUMID = 0xF2
    BME280_REGISTER_STATUS = 0XF3
    BME280_REGISTER_CONTROL = 0xF4
    BME280_REGISTER_CONFIG = 0xF5
    BME280_REGISTER_PRESSURE_DATA = 0xF7
    BME280_REGISTER_TEMP_DATA = 0xFA
    BME280_REGISTER_HUMID_DATA = 0xFD

    oversampling = {
        1: 1,
        2: 2,
        4: 3,
        8: 4,
        16: 5
    }

    mode = {
        1: 0,  # sleep
        2: 1,  # forced
        4: 2  # normal
    }

    def __init__(self, bus: SMBus):
        self.bus: SMBus = bus

        # Read blocks of calibration data from EEPROM
        cal1 = bus.read_i2c_block_data(BME280_ADDRESS, self.BME280_REGISTER_DIG_T1, 24)
        cal2 = bus.read_i2c_block_data(BME280_ADDRESS, self.BME280_REGISTER_DIG_H1, 1)
        cal3 = bus.read_i2c_block_data(BME280_ADDRESS, self.BME280_REGISTER_DIG_H2, 7)

        # Convert byte data to word values
        self.dig_T1 = get_ushort(cal1, 0)
        self.dig_T2 = get_short(cal1, 2)
        self.dig_T3 = get_short(cal1, 4)

        self.dig_p = []
        self.dig_P1 = get_ushort(cal1, 6)
        for i in range(8, 24, 2):
            self.dig_p.append(get_short(cal1, i))

        self.dig_H1 = get_uchar(cal2, 0)
        self.dig_H2 = get_short(cal3, 0)
        self.dig_H3 = get_uchar(cal3, 2)

        self.dig_H4 = get_char(cal3, 3)
        self.dig_H4 = (self.dig_H4 << 24) >> 20
        self.dig_H4 = self.dig_H4 | (get_char(cal3, 4) & 0x0F)

        self.dig_H5 = get_char(cal3, 5)
        self.dig_H5 = (self.dig_H5 << 24) >> 20
        self.dig_H5 = self.dig_H5 | (get_uchar(cal3, 4) >> 4 & 0x0F)

        self.dig_H6 = get_char(cal3, 6)

        # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
        self.oversampling_temp = 2
        self.oversampling_pres = 2
        self.oversampling_hum = 2
        self.set_humidity_oversampling(2)
        self.set_pressure_oversampling(2)
        self.set_temperature_oversampling(2)
        self.set_control_mode(2)

    def id(self):
        # Chip ID Register Address
        chip_id, chip_version = self.bus.read_i2c_block_data(BME280_ADDRESS, self.BME280_REGISTER_CHIP_ID, 2)
        return chip_id, chip_version

    def _calculate_wait_time(self):
        self.wait_time = 1.25 + (2.3 * self.oversampling_temp) + \
                         ((2.3 * self.oversampling_pres) + 0.575) + \
                         ((2.3 * self.oversampling_hum) + 0.575)

    def set_humidity_oversampling(self, value: int):
        if value not in (1, 2, 4, 8, 16):
            return
        self.oversampling_hum = value
        self._calculate_wait_time()
        self.bus.write_byte_data(BME280_ADDRESS,
                                 self.BME280_REGISTER_CONTROL_HUMID,
                                 self.oversampling[value])

    def set_pressure_oversampling(self, value: int):
        if value not in (1, 2, 4, 8, 16):
            return
        self.oversampling_pres = value
        self._calculate_wait_time()
        temp = self.bus.read_i2c_block_data(BME280_ADDRESS,
                                            self.BME280_REGISTER_CONTROL,
                                            1)
        temp = (self.oversampling[value] << 2) | temp[0]
        self.bus.write_byte_data(BME280_ADDRESS,
                                 self.BME280_REGISTER_CONTROL,
                                 temp)

    def set_temperature_oversampling(self, value: int):
        if value not in (1, 2, 4, 8, 16):
            return
        self.oversampling_temp = value
        self._calculate_wait_time()
        temp = self.bus.read_i2c_block_data(BME280_ADDRESS,
                                            self.BME280_REGISTER_CONTROL,
                                            1)
        temp = (self.oversampling[value] << 5) | temp[0]
        self.bus.write_byte_data(BME280_ADDRESS,
                                 self.BME280_REGISTER_CONTROL,
                                 temp)

    def set_control_mode(self, value: int):
        if value not in (1, 2, 4):
            return
        temp = self.bus.read_i2c_block_data(BME280_ADDRESS,
                                            self.BME280_REGISTER_CONTROL,
                                            1)
        temp = self.mode[value] | temp[0]
        self.bus.write_byte_data(BME280_ADDRESS,
                                 self.BME280_REGISTER_CONTROL,
                                 temp)

    def read_all(self):
        self.set_control_mode(2)
        time.sleep(self.wait_time / 1000)

        # Read temperature/pressure/humidity
        data = self.bus.read_i2c_block_data(BME280_ADDRESS, self.BME280_REGISTER_PRESSURE_DATA, 8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        # Refine temperature
        var1 = (((temp_raw >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
        var2 = (((((temp_raw >> 4) - self.dig_T1) *
                  ((temp_raw >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        t_fine = var1 + var2
        temperature = float(((t_fine * 5) + 128) >> 8)

        # Refine pressure and adjust for temperature
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self.dig_p[4] / 32768.0
        var2 = var2 + var1 * self.dig_p[3] * 2.0
        var2 = var2 / 4.0 + self.dig_p[2] * 65536.0
        var1 = (self.dig_p[2] * var1 * var1 / 524288.0 + self.dig_p[0] * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1
        if var1 == 0:
            pressure = 0
        else:
            pressure = 1048576.0 - pres_raw
            pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = self.dig_p[7] * pressure * pressure / 2147483648.0
            var2 = pressure * self.dig_p[6] / 32768.0
            pressure = pressure + (var1 + var2 + self.dig_p[5]) / 16.0

        # Refine humidity
        humidity = t_fine - 76800.0
        humidity = (hum_raw - (self.dig_H4 * 64.0 + self.dig_H5 / 16384.0 * humidity)) * (self.dig_H2 / 65536.0 *
                                                                                          (
                                                                                                  1.0 + self.dig_H6 / 67108864.0 * humidity * (
                                                                                                  1.0 + self.dig_H3 / 67108864.0 * humidity)))
        humidity = humidity * (1.0 - self.dig_H1 * humidity / 524288.0)
        if humidity > 100:
            humidity = 100
        elif humidity < 0:
            humidity = 0

        return temperature / 100.0, pressure / 100.0, humidity


def main():
    bus = SMBus(1)  # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
    # Rev 1 Pi uses bus 0

    bme280 = BME280(bus)
    chip_id, chip_version = bme280.id()
    print(f"Chip ID     : {chip_id}")
    print(f"Version     : {chip_version}")

    temperature, pressure, humidity = bme280.read_all()

    print(f"Temperature : {temperature} C")
    print(f"Pressure    : {round(pressure, 3)} hPa")
    print(f"Humidity    : {round(humidity, 2)} %")


if __name__ == "__main__":
    main()
