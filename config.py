from configparser import ConfigParser, NoSectionError
from os.path import dirname, join
from sys import argv

PATH = join(dirname(argv[0]), 'config.ini')

conf = ConfigParser()
conf.read(PATH)

if not conf.has_section("sensors"):
    raise Exception("There is no \"sensors\" section in config file!")
else:
    sensors = []
    for name in ("bme280", "ms5611", "max6675"):
        if conf.has_option("sensors", name):
            sensors.append(name)

