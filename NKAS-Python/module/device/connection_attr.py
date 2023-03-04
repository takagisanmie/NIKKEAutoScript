from adbutils import AdbClient, AdbDevice
import uiautomator2 as u2
from cached_property import cached_property

import glo


class ConnectionAttr:
    def __init__(self, config):
        self.config = config

    @cached_property
    def u2(self) -> u2.Device:
        self.adb_client.device_list()
        serial = str(self.config.Simulator_Serial)
        if serial.startswith('emulator-') or serial.startswith('127.0.0.1:'):
            device = u2.connect_usb(serial)
        else:
            device = u2.connect(serial)
        device.set_new_command_timeout(604800)
        return device

    @cached_property
    def adb_client(self) -> AdbClient:
        from adbutils import adb as adb_client
        # host = '127.0.0.1'
        # port = 5037
        # return AdbClient(host, port)
        return adb_client

    @cached_property
    def adb(self) -> AdbDevice:
        serial = str(self.config.Simulator_Serial)
        return AdbDevice(self.adb_client, serial)
