import time

from module.device.connection_attr import ConnectionAttr


class Connection(ConnectionAttr):
    def __init__(self, config):
        super().__init__(config)
        self.package = self.config.Emulator_PackageName


    @staticmethod
    def sleep(second):
        time.sleep(second)
