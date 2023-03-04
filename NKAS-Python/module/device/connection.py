import time

from module.device.connection_attr import ConnectionAttr


class Connection(ConnectionAttr):
    def __init__(self, config):
        super().__init__(config)
        self.jp_package = self.config.Emulator_JP_PackageName
        self.tw_package = self.config.Emulator_TW_PackageName

    def adb_restart(self):
        from adbutils import adb as adb_client
        adb_client.server_kill()
        adb_client._connect(timeout=10)
        self.sleep(5)

    @staticmethod
    def sleep(second):
        time.sleep(second)
