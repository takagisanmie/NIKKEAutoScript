from common.enum.enum import *
from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from module.task.commission.commission_assets import *


class Commission(UI, Task):
    def run(self):
        self.LINE('Commission')
        self.go(destination=page_outpost_commission)
        self.getReward()
        self.finish(self.config, 'Commission')
        self.INFO('Commission is finished')

    def getReward(self, restart=True):
        print(restart)
        self.device.sleep(3)
        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(0.8)

        while 1:
            self.device.screenshot()
            if click_timer.reached() and self.device.appear_then_click(to_commission):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(receive_reward):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(send_commission):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(send_commission_confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if confirm_timer.reached():
                if restart:
                    if self.device.appear_then_click(commission_close):
                        return self.getReward(restart=False)
                else:
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
