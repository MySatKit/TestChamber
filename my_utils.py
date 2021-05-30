from ctypes import c_short


def get_short(data, index):
    # return two bytes from data as a signed 16-bit value
    return c_short((data[index + 1] << 8) + data[index]).value


def get_ushort(data, index):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index + 1] << 8) + data[index]


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