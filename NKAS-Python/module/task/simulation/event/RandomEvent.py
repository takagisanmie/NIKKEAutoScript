import glo
from assets import *
from common.exception import Timeout
from module.task.simulation.base.event_base import BaseEvent
from module.task.simulation.simulation_assets import *
from module.tools.timer import Timer


class RandomEvent(BaseEvent):
    def run(self):
        print('RandomEvent')
        self.INFO('start RandomEvent')

        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        reset_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        glo.set_value('RandomEvent', [])
        mask_id = 'RandomEvent'

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(Random):
                timeout.reset()
                confirm_timer.reset()
                continue

            # 在选择具体事件
            if self.device.appear_then_click(random_option, mask_id=mask_id, once=True):
                self.device.sleep(1)
                timeout.reset()
                confirm_timer.reset()

            # 在替换相同效果
            if self.device.appear(limited) and self.device.appear(cancel):
                self.parent._skip()
                return

            # 在替换相同效果
            if self.device.appear(replacement):
                self.parent.skip()
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                return

            # 需要选择一个效果，进行操作 or 选择效果升级
            if self.device.appear(need_to_choose) or self.device.appear(need_to_improve):
                self.parent.getPreferentialEffect()
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                return

            # 不选择
            if self.device.appear(cancel):
                self.parent.skip()
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                return

            if self.device.appear(no_condition) and self.device.appear(cancel):
                self.parent.skip()
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

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

            if reset_timer.reached():
                reset_timer.reset()
                glo.set_value(mask_id, [])

    def _skip(self):
        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=4).start()
        reset_timer = Timer(2, count=6).start()
        click_timer = Timer(1.2)

        glo.set_value('_skip', [])
        mask_id = '_skip'

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(cancel, mask_id=mask_id):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(confirm, mask_id=mask_id):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

            if reset_timer.reached():
                reset_timer.reset()
                glo.set_value(mask_id, [])
