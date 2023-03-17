from common.exception import Timeout
from module.base.task import Task
from module.task.commission.commission_assets import *
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI


class Commission(UI, Task):
    def run(self):
        self.LINE('Commission')
        self.go(destination=page_outpost_commission)
        self.getReward()
        self.finish(self.config, 'Commission')
        self.INFO('Commission is finished')
        self.go(page_main)

    def getReward(self, restart=True):
        self.device.sleep(4)
        timeout = Timer(20).start()
        confirm_timer = Timer(3, count=3).start()
        click_timer = Timer(1.2)

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
                    self.device.sleep(3)
                    if self.device.appear_then_click(commission_close):
                        return self.getReward(restart=False)
                else:
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
