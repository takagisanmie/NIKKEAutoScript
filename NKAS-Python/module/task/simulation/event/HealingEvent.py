
from common.enum.enum import *
from assets import *
from common.exception import Timeout
from module.task.simulation.base.event_base import BaseEvent
from module.tools.timer import Timer
from module.task.simulation.simulation_assets import *


class HealingEvent(BaseEvent):
    def run(self):
        print('HealingEvent')
        self.INFO('start HealingEvent')

        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(Healing):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(healing_option):
                timeout.reset()
                confirm_timer.reset()

            if click_timer.reached() and self.device.appear_then_click(confirm, 0.84):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(reset_time):
                if confirm_timer.reached():
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
