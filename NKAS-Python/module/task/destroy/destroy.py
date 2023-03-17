from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from module.task.destroy.destroy_assets import _destroy


class Destroy(UI, Task):
    def run(self):
        self.LINE('Destroy')
        self.go(destination=page_destroy)
        self.destroy()
        self.INFO('Destroy has no free chance')
        self.finish(self.config, 'Destroy')
        self.INFO('Destroy is finished')
        self.go(page_main)

    def destroy(self):

        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(_destroy, value=0.92):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

            if click_timer.reached() and self.device.hide(destroy_sign) and self.device.multiClickLocation((300, 300)):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

            if self.device.appear(destroy_sign) and confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
