import uiautomator2 as u2

from cached_property import cached_property

import glo


class ConnectionAttr:
    def __init__(self, config):
        self.config = config

    @cached_property
    def u2(self) -> u2.Device:
        self.checkDevices()
        self.serial = str(self.config.Simulator_Serial)
        try:
            if self.serial.startswith('emulator-') or self.serial.startswith('127.0.0.1:'):
                device = u2.connect_usb(self.serial)
            else:
                device = u2.connect(self.serial)
            device.set_new_command_timeout(604800)
            return device
        except Exception as e:
            glo.getNKAS().socket.emit('insertLog', glo.getSocket().getLog('ERROR', f'连接模拟器失败: {str(e)}'))

    @staticmethod
    def checkDevices():
        import subprocess
        subprocess.run("adb devices", stdout=subprocess.PIPE, shell=True)
