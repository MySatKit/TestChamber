from smbus2 import SMBus
from PyQt6.QtWidgets import QMainWindow, QRadioButton
from PyQt6.QtCore import QThread

from GUI.main_window import Ui_MainWindow
from Hardware import RelayDriver
from Hardware.bme280 import BME280
from Hardware.ms5611 import MS5611


class App(Ui_MainWindow, QMainWindow):

    def __init__(self):
        super(App, self).__init__()
        self.setupUi(self)

        # states
        self.light_state: bool = False
        self.cooler_state: bool = False
        self.pressure_state: bool = False

        # ------- i2c driver section ------------------------
        self.i2c_bus = SMBus(1)
        self.inside_sensor_driver = MS5611(self.i2c_bus)
        self.outside_sensor_driver = BME280(self.i2c_bus)
        self.inside_thread = QThread()
        self.outside_thread = QThread()

        # data
        self.inside_pressure: float = 0
        self.outside_pressure: float = 0
        self.inside_temp: float = 0
        self.outside_temp: float = 0
        self.outside_humidity: float = 0
        # ---------------------------------------------------

        # GPIO drivers
        self.pressure_driver = RelayDriver(11)
        self.cooler_driver = RelayDriver(13)
        self.light_driver = RelayDriver(15)

        self.setup()
        self.inside_thread.start()
        self.outside_thread.start()

    def setup(self):
        self.inside_thread.started.connect(self.inside_thread_routine)
        self.outside_thread.started.connect(self.outside_thread_routine)

    def inside_thread_routine(self):
        while True:
            self.inside_pressure, self.inside_temp = self.inside_sensor_driver.read_all()
            self.inside_pressure = round(self.inside_pressure, 3)
            self.data_table.item(0, 1).setText(self.inside_temp)
            self.data_table.item(1, 1).setText(self.inside_pressure)
            self.inside_thread.msleep(500)

    def outside_thread_routine(self):
        while True:
            self.outside_temp, self.outside_pressure, self.outside_humidity = self.outside_sensor_driver.read_all()
            self.outside_pressure = round(self.outside_pressure, 3)
            self.outside_humidity = round(self.outside_humidity, 2)
            self.data_table.item(0, 0).setText(self.outside_temp)
            self.data_table.item(1, 0).setText(self.outside_pressure)
            self.data_table.item(2, 0).setText(self.outside_humidity)
            height = 44330.0 * (1.0 - (self.inside_pressure / self.outside_pressure)**0.1903)
            self.height_panel.display(f"{height} m")
            self.outside_thread.msleep(100)

    def cooler_state_slot(self, radio_btn: QRadioButton):
        match radio_btn.text().lower():
            case "on":
                self.cooler_state = True
            case "off":
                self.cooler_state = False
        self.cooler_driver.update(self.cooler_state)

    def pressure_state_slot(self, radio_btn: QRadioButton):
        match radio_btn.text().lower():
            case "on":
                self.pressure_state = True
            case "off":
                self.pressure_state = False
        self.pressure_driver.update(self.pressure_state)

    def light_state_slot(self, radio_btn: QRadioButton):
        match radio_btn.text().lower():
            case "on":
                self.light_state = True
            case "off":
                self.light_state = False
        self.light_driver.update(self.cooler_state)
