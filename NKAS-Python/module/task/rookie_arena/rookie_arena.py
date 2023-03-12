from common.enum.enum import *
from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from module.task.rookie_arena.rookie_arena_assets import *


class RookieArena(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = self.config.get('Task.RookieArena.target', self.config.Task_Dict)

    def run(self):
        self.LINE('Rookie Arena')
        self.go(destination=page_rookie_arena)
        if self.device._hide(free_chance):
            self._finish()
            return
        self.choose_target()
        self._finish()

    def _finish(self):
        self.finish(self.config, 'RookieArena')
        self.INFO('Rookie Arena is finished')

    def choose_target(self):
        timeout = Timer(90).start()
        confirm_timer = Timer(1, count=5).start()
        click_timer = Timer(1.2)

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

            if click_timer.reached() and self.device.appear(end_battle) and self.device.uiautomator_click(300, 300):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.appear(rookie_arena_sign) and confirm_timer.reached():
                self.INFO('Rookie Arena has no free chance')
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
