from ctypes import c_short
from typing import Union


def get_short(data: Union[list, tuple], index: int):
    # return two bytes from data as a signed 16-bit value
    return c_short((data[index + 1] << 8) + data[index]).value


def get_ushort_le(data: Union[list, tuple], index: int):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index + 1] << 8) + data[index]


def get_ushort_be(data: Union[list, tuple], index: int):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index] << 8) + data[index + 1]


def get_char(data: Union[list, tuple], index: int):
    # return one byte from data as a signed char
    result = data[index]
    if result > 127:
        result -= 256
    return result


def get_uchar(data: Union[list, tuple], index: int):
    # return one byte from data as an unsigned char
    result = data[index] & 0xFF
    return result