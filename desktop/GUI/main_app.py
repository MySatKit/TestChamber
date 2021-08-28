from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QLineEdit, QWidget, QComboBox
from typing import Dict

from .widgets import Ui_MainWindow
from desktop.drivers import spi_drivers, i2c_drivers


class TestChamberApp(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(TestChamberApp, self).__init__()
        self.setupUi(self)
        self.bind_actions()

        self.i2c_scroll_area_layout = QVBoxLayout()
        self.i2c_devices_lists_dict: Dict[QComboBox, str] = {}

        self.spi_scroll_area_layout = QVBoxLayout()
        self.spi_devices_lists_dict: Dict[QComboBox, str] = {}

        self.bind_layouts()

    def bind_actions(self):
        self.actionI2C_device.triggered.connect(self.new_i2c_device)
        self.actionSPI_device.triggered.connect(self.new_spi_device)
        self.actionWeb_Camera.triggered.connect(self.new_web_camera)
        self.actionGPIO_controller.triggered.connect(self.new_gpio_controller)

        self.actionUpdate_I2C_devices_list.triggered.connect(self.update_i2c_devices_list)

    def bind_layouts(self):
        self.i2c_scrollAreaWidgetContents.setLayout(self.i2c_scroll_area_layout)
        self.spi_scrollAreaWidgetContents.setLayout(self.spi_scroll_area_layout)

    @staticmethod
    def new_basic_device(name: str, value: QWidget) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        name_line = QLineEdit()
        name_line.setText(name)
        layout.addWidget(name_line)
        layout.addWidget(value)
        return layout

    @staticmethod
    def get_i2c_device_drivers() -> QComboBox:
        widget = QComboBox()
        widget.addItem("Driver", None)
        widget.addItems(i2c_drivers)
        return widget

    @staticmethod
    def get_spi_device_drivers() -> QComboBox:
        widget = QComboBox()
        widget.addItem("Driver", None)
        widget.addItems(spi_drivers)
        return widget

    # Action functions -------------------------------------------
    def new_i2c_device(self):
        # create and save new i2c drop-menu
        new_value = QComboBox()
        self.i2c_devices_lists_dict[new_value] = 'name'
        self.update_i2c_devices_list()

        new_row = self.new_basic_device('name', new_value)
        new_row.addWidget(self.get_i2c_device_drivers())
        self.i2c_scroll_area_layout.addLayout(new_row)

    def new_spi_device(self):
        # create and save new i2c drop-menu
        new_value = QComboBox()
        self.spi_devices_lists_dict[new_value] = 'name'
        self.update_spi_devices_list()

        new_row = self.new_basic_device('name', new_value)
        new_row.addWidget(self.get_spi_device_drivers())
        self.spi_scroll_area_layout.addLayout(new_row)

    def new_web_camera(self):
        pass

    def new_gpio_controller(self):
        pass

    def update_i2c_devices_list(self) -> None:
        addresses_list = ['Address']  # ToDo - get devices and update devices list
        for i2c_devices_list in self.i2c_devices_lists_dict:
            items = [i2c_devices_list.itemText(i) for i in range(i2c_devices_list.count())]
            for addr in addresses_list:
                if addr not in items:
                    if addr == 'Address':
                        i2c_devices_list.addItem(addr, None)
                    else:
                        i2c_devices_list.addItem(addr, addr)

    def update_spi_devices_list(self) -> None:
        addresses_list = ['CE0', 'CE1', 'CE2']
        for spi_devices_list in self.spi_devices_lists_dict:
            items = [spi_devices_list.itemText(i) for i in range(spi_devices_list.count())]
            for addr in addresses_list:
                if addr not in items:
                    spi_devices_list.addItem(addr, addr)

    # Action functions end --------------------------------------
