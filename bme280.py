#!/usr/bin/python

import time
from ctypes import c_short
from smbus2 import SMBus

DEVICE_ADDR = 0x76  # Default device I2C address


def get_short(data, index):
    # return two bytes from data as a signed 16-bit value
    return c_short((data[index+1] << 8) + data[index]).value


def get_ushort(data, index):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index+1] << 8) + data[index]


def get_char(data, index):
    # return one byte from data as a signed char
    result = data[index]
    if result > 127:
        result -= 256
    return result


def get_uchar(data, index):
    # return one byte from data as an unsigned char
    result = data[index] & 0xFF
    return result


def read_BME280_ID(bus: SMBus, addr=DEVICE_ADDR):
    # Chip ID Register Address
    REG_ID = 0xD0
    chip_id, chip_version = bus.read_i2c_block_data(addr, REG_ID, 2)
    return chip_id, chip_version


def read_BME280_all(bus: SMBus, addr=DEVICE_ADDR):
    # Register Addresses
    REG_DATA = 0xF7
    REG_CONTROL = 0xF4
    REG_CONFIG = 0xF5

    REG_CONTROL_HUM = 0xF2
    REG_HUM_MSB = 0xFD
    REG_HUM_LSB = 0xFE

    # Oversample setting - page 27
    OVERSAMPLE_TEMP = 2
    OVERSAMPLE_PRES = 2
    MODE = 1

    # Oversample setting for humidity register - page 26
    OVERSAMPLE_HUM = 2
    bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

    control = OVERSAMPLE_TEMP << 5 | OVERSAMPLE_PRES << 2 | MODE
    bus.write_byte_data(addr, REG_CONTROL, control)

    # Read blocks of calibration data from EEPROM
    # See Page 22 data sheet
    cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
    cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
    cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

    # Convert byte data to word values
    dig_T1 = get_ushort(cal1, 0)
    dig_T2 = get_short(cal1, 2)
    dig_T3 = get_short(cal1, 4)

    dig_p = []
    dig_P1 = get_ushort(cal1, 6)
    for i in range(8, 24, 2):
        dig_p.append(get_short(cal1, i))

    dig_H1 = get_uchar(cal2, 0)
    dig_H2 = get_short(cal3, 0)
    dig_H3 = get_uchar(cal3, 2)

    dig_H4 = get_char(cal3, 3)
    dig_H4 = (dig_H4 << 24) >> 20
    dig_H4 = dig_H4 | (get_char(cal3, 4) & 0x0F)

    dig_H5 = get_char(cal3, 5)
    dig_H5 = (dig_H5 << 24) >> 20
    dig_H5 = dig_H5 | (get_uchar(cal3, 4) >> 4 & 0x0F)

    dig_H6 = get_char(cal3, 6)

    # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
    wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 *
                                                   OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
    time.sleep(wait_time/1000)  # Wait the required time

    # Read temperature/pressure/humidity
    data = bus.read_i2c_block_data(addr, REG_DATA, 8)
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    hum_raw = (data[6] << 8) | data[7]

    # Refine temperature
    var1 = ((((temp_raw >> 3)-(dig_T1 << 1)))*(dig_T2)) >> 11
    var2 = (((((temp_raw >> 4) - (dig_T1)) *
            ((temp_raw >> 4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
    t_fine = var1+var2
    temperature = float(((t_fine * 5) + 128) >> 8)

    # Refine pressure and adjust for temperature
    var1 = t_fine / 2.0 - 64000.0
    var2 = var1 * var1 * dig_p[4] / 32768.0
    var2 = var2 + var1 * dig_p[3] * 2.0
    var2 = var2 / 4.0 + dig_p[2] * 65536.0
    var1 = (dig_p[2] * var1 * var1 / 524288.0 + dig_p[0] * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * dig_P1
    if var1 == 0:
        pressure = 0
    else:
        pressure = 1048576.0 - pres_raw
        pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
        var1 = dig_p[7] * pressure * pressure / 2147483648.0
        var2 = pressure * dig_p[6] / 32768.0
        pressure = pressure + (var1 + var2 + dig_p[5]) / 16.0

    # Refine humidity
    humidity = t_fine - 76800.0
    humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 *
                                                                            (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
    humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
    if humidity > 100:
        humidity = 100
    elif humidity < 0:
        humidity = 0

    return temperature/100.0, pressure/100.0, humidity


def main():
    bus = SMBus(1)  # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
    # Rev 1 Pi uses bus 0

    chip_id, chip_version = read_BME280_ID(bus)
    print(f"Chip ID     : {chip_id}")
    print(f"Version     : {chip_version}")

    temperature, pressure, humidity = read_BME280_all(bus)

    print(f"Temperature : {temperature} C")
    print(f"Pressure    : {round(pressure, 3)} hPa")
    print(f"Humidity    : {round(humidity, 2)} %")


if __name__ == "__main__":
    main()
