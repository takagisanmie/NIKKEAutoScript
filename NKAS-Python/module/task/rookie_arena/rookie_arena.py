from common.enum.enum import *
from common.exception import Timeout
from module.base.task import Task
from module.task.rookie_arena.rookie_arena_assets import *
from module.tools.match import resize
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI


class RookieArena(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = self.config.get('Task.RookieArena.target', self.config.Task_Dict)
        under = self.config.get('Task.RookieArena.under', self.config.Task_Dict)
        self.under = int(under) if under else 0
        refresh_chance = self.config.get('Task.RookieArena.refresh_chance', self.config.Task_Dict)
        self.refresh_chance = int(refresh_chance) if refresh_chance else 1
        self.index = -1

    def run(self):
        self.LINE('Rookie Arena')
        self.go(destination=page_rookie_arena)
        if self.device._hide(free_chance):
            self._finish()
            return

        self.execute()
        self._finish()

    def _finish(self):
        self.finish(self.config, 'RookieArena')
        self.INFO('Rookie Arena is finished')
        self.go(page_main)

    def execute(self):
        timeout = Timer(90).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear(free_chance, once=True):
                self.choose_target()
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()

            if self.device.appear(rookie_arena_sign) and confirm_timer.reached():
                self.INFO('Rookie Arena has no free chance')
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def choose_target(self):
        timeout = Timer(90).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        refresh_chance = self.refresh_chance

        if self.under:
            while 1:
                self.device.screenshot()
                self.compare()
                if self.device.appear_then_click(into_battle):
                    timeout.reset()
                    confirm_timer.reset()
                    click_timer.reset()

                    while 1:
                        self.device.screenshot()

                        if self.device.appear_then_click(into_battle):
                            timeout.reset()
                            confirm_timer.reset()
                            click_timer.reset()
                            continue

                        if click_timer.reached() \
                                and self.device.appear(end_battle) \
                                and self.device.uiautomator_click(300, 300):
                            timeout.reset()
                            confirm_timer.reset()
                            click_timer.reset()
                            self.device.sleep(8)
                            continue

                        if self.device.appear(rookie_arena_sign) and confirm_timer.reached():
                            return

                self.device.sleep(1.2)
                self.device.screenshot()
                self.device.appear_then_click(refresh)
                self.device.sleep(1.2)
                refresh_chance -= 1
                self.INFO(f'rest refresh chance: {refresh_chance}')
                if not refresh_chance:
                    break

        timeout.reset()
        confirm_timer.reset()
        click_timer.reset()

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(save_formation):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(free_chance, index=self.target - 1):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(into_battle):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() \
                    and self.device.appear(end_battle) \
                    and self.device.uiautomator_click(300, 300):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                self.device.sleep(8)
                continue

            if self.device.appear(rookie_arena_sign) and confirm_timer.reached():
                return

    def compare(self, target_list=None):

        timeout = Timer(90).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        if not target_list:
            target_list = self.device.appear(free_chance, _result=ImgResult.ALL_RESULT)

        target = target_list[0]['location']

        already_compared = False

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.hide(formation_sign) and self.device.multiClickLocation(target, 1):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear(formation_sign):
                self.device.sleep(1.2)
                self.device.screenshot()
                own_power = int(self.device.textStrategy(None, own_power_area, OcrResult.TEXT, line=True))
                target_tower = int(self.device.textStrategy(None, target_power_area, OcrResult.TEXT, line=True))
                self.INFO(f'own power: {own_power}')
                self.INFO(f'target power: {target_tower}')
                self.INFO(f'target index: {3 - len(target_list) + 1}')
                if own_power - self.under > target_tower:
                    return

                already_compared = True

            if already_compared and self.device.appear_then_click(close_formation):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if already_compared and self.device.hide(close_formation):
                target_list = target_list[1:]
                if target_list:
                    return self.compare(target_list)
                else:
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
