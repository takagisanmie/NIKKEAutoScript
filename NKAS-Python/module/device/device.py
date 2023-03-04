import glo
from module.device.control import Control


class Device(Control):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        glo.set_value('device', self)


    def app_start(self, package_name=None):
        return self.app_start_uiautomator2(package_name)
