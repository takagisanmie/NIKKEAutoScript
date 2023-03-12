import glo
from common.enum.enum import *
from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer, getTaskResetTime
from module.ui.page import *
from module.ui.ui import UI
from module.task.daily.daily_assets import *


class Daily(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.equipmentUpgrade = int(self.config.get('Task.Daily.equipmentUpgrade', self.config.Task_Dict))
        self.nikkeUpgrade = int(self.config.get('Task.Daily.nikkeUpgrade', self.config.Task_Dict))

    def run(self):
        self.LINE('Daily')
        if self.equipmentUpgrade:
            self.improve_equipment()
        self.to_liberation()
        self.go(destination=page_daily)
        self.getReward()
        self.to_pass()
        self.finish(self.config, 'Daily')
        self.INFO('Daily is finished')

    def getReward(self):
        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=8).start()
        reset_timer = Timer(1, count=8).start()
        click_timer = Timer(1.2)

        glo.set_value('getReward', [])
        mask_id = 'getReward'

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(reward, value=0.8):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(get):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(emphasis, img_template=emphasis_area,
                                                                       mask_id=mask_id):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                return

            if reset_timer.reached():
                reset_timer.reset()
                glo.set_value(mask_id, [])

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def improve_equipment(self):
        self.go(destination=page_inventory)
        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=3).start()
        reset_timer = Timer(1, count=8).start()
        click_timer = Timer(1.2)

        glo.set_value('improve_equipment', [])
        mask_id = 'improve_equipment'

        is_finished = False

        while 1:
            self.device.screenshot()

            if not is_finished and click_timer.reached() and self.device.appear_then_click(equipment, mask_id=mask_id):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not is_finished \
                    and click_timer.reached() \
                    and self.device.appear(inventory_sign) \
                    and self.device.appear_then_click(Level_0):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not is_finished and click_timer.reached() and self.device.appear_then_click(improve):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(confirm_improvement):
                is_finished = True
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not is_finished and click_timer.reached() \
                    and (self.device.appear_then_click(normal_materials)
                         or self.device.appear_then_click(advanced_materials)):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if is_finished and click_timer.reached() and self.device.appear_then_click(close_equipment):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if is_finished and self.device.appear(inventory_sign) and confirm_timer.reached():
                return

            if reset_timer.reached():
                reset_timer.reset()
                glo.set_value(mask_id, [])

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def to_liberation(self):
        self.go(page_liberation)

        timeout = Timer(10).start()
        confirm_timer = Timer(3, count=8).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.clickTextLocation('_完成'):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def to_pass(self):
        self.go(page_pass)

        timeout = Timer(10).start()
        confirm_timer = Timer(3, count=8).start()
        reset_timer = Timer(1, count=24).start()
        click_timer = Timer(1.2)

        glo.set_value('pass', [])
        mask_id = 'pass'

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(reward, value=0.8):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(pass_get):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(pass_mission, img_template=pass_area,
                                                                       mask_id=mask_id):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(pass_reward, img_template=pass_area,
                                                                       mask_id=mask_id):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

            if reset_timer.reached():
                reset_timer.reset()
                glo.set_value(mask_id, [])
