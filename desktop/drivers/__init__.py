from .ms5611 import MS5611
from .bme280 import BME280
from .max6675 import Max6675


spi_drivers = ["Max6675"]
i2c_drivers = ["MS5611", "BME280"]
__all__ = ["Max6675", "MS5611", "BME280", "spi_drivers", "i2c_drivers"]
