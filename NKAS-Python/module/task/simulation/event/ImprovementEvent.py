
from common.enum.enum import *
from common.exception import Timeout

from module.task.simulation.base.event_base import BaseEvent
from module.tools.timer import Timer
from assets import *
from module.task.simulation.simulation_assets import *


class ImprovementEvent(BaseEvent):
    def run(self):
        print('ImprovementEvent')
        self.INFO('start ImprovementEvent')

        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(Improvement):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            # 不满足选项
            if self.device.appear(no_condition):
                self.parent.skip()
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                return

            if click_timer.reached() and self.device.appear_then_click(improvement_option):
                timeout.reset()
                confirm_timer.reset()

            # 需要选择一个效果，进行操作
            if self.device.appear(need_to_choose) or self.device.appear(need_to_improve):
                self.parent.getPreferentialEffect()
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                return

            if click_timer.reached() and self.device.appear_then_click(confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(reset_time):
                if confirm_timer.reached():
                    return

            # 不满足选项
            if self.device.hide(improvement_option):
                if self.device.appear(cancel):
                    self.parent.skip()
                    timeout.reset()
                    click_timer.reset()
                    confirm_timer.reset()
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def need_to_choose(self):
        pass
