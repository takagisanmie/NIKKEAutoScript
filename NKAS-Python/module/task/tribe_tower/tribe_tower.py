from common.enum.enum import *
from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from module.task.tribe_tower.tribe_tower_assets import *


class TribeTower(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daily = int(self.config.get('Task.TribeTower.daily', self.config.Task_Dict))
        self.is_finished = False

    def run(self):
        self.LINE('Tribe Tower')
        self.go(destination=page_tribe_tower)
        list = [Elysion, Missilis, Tetra, Pilgrim]
        company_list = self.device.appear(template=list, value=0.9,
                                          _result=ImgResult.ALL_RESULT, sort_by='left')
        self.choose_tower(company_list)
        self._finish()

    def choose_tower(self, company_list):
        timeout = Timer(120).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        company = company_list[0]['template']
        flag = True

        while 1:
            self.device.screenshot()
            if flag and self.device.hide(company):
                flag = False
                company_list = company_list[1:]
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if flag and click_timer.reached() and self.device.appear_then_click(company):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.appear(rest_chance_sign) and self.device.appear(stage):
                self.tower(company)

                if self.is_finished:
                    return

                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear(tribe_tower_sign) and confirm_timer.reached():
                if len(company_list):
                    return self.choose_tower(company_list)
                else:
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def tower(self, template):
        timeout = Timer(120).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        self.checkRestChance(template)

        failed = False

        while 1:
            self.device.screenshot()

            if not failed and self.device.appear(auto, gray=True):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

                if self.daily:
                    self.end_battle()

                self.device.sleep(5)
                continue

            if (not failed and self.rest_chance) \
                    and click_timer.reached() \
                    and self.device._hide(stage_large) \
                    and self.device.appear(rest_chance_sign) \
                    and self.device.uiautomator_click(350, 550):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if (not failed and self.rest_chance) \
                    and click_timer.reached() \
                    and self.device.appear(stage_large) \
                    and self.device.appear_then_click(into_battle):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if not failed and self.device.appear(operation_failed) and self.device.appear_then_click(end_battle_back):
                failed = True

                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

                if self.daily:
                    self.is_finished = True

                else:
                    self.WARNING(f'current battle in {template["id"]} tower is failed')
                    self.WARNING('NKAS will go to the next company tower')

                continue

            if self.device.appear(end_battle):
                self.rest_chance -= 1
                self.INFO(f'rest chance: {self.rest_chance}')
                self.device.sleep(3)

            if not failed \
                    and click_timer.reached() \
                    and (self.device.appear_then_click(next_stage) or self.device.appear_then_click(end_battle)):
                self.device.sleep(5)
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if (not failed and self.rest_chance) \
                    and click_timer.reached() \
                    and self.device.appear(stage_large) \
                    and self.device.appear_then_click(into_battle):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if (failed or not self.rest_chance) \
                    and click_timer.reached() \
                    and confirm_timer.reached() \
                    and self.device._hide(tribe_tower_sign) \
                    and self.device.appear_then_click(back):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            # 礼包
            if click_timer.reached() and self.device.appear(gift) and self.device.appear_then_click(confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(gift):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(tribe_tower_sign) and confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def checkRestChance(self, template):
        self.device.sleep(2)
        self.device.screenshot()
        self.rest_chance = self.device.textStrategy(None, rest_chance, OcrResult.TEXT, line=True)
        self.rest_chance = int(self.rest_chance)
        if self.rest_chance > 0:
            self.INFO(f'{template["id"]} tower')
            self.INFO(f'rest chance: {self.rest_chance}')
            return True

    def end_battle(self):
        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(pause):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(abandon):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.appear(operation_failed) and confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def _finish(self):
        self.finish(self.config, 'TribeTower')
        self.INFO('Tribe Tower is finished')
        self.go(page_main)
