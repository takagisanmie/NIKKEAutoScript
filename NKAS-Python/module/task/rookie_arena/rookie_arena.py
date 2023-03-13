import glo
from common.enum.enum import *
from common.exception import Timeout
from module.base.task import Task
from module.tools.match import resize
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from module.task.rookie_arena.rookie_arena_assets import *


class RookieArena(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = self.config.get('Task.RookieArena.target', self.config.Task_Dict)
        self.under = int(self.config.get('Task.RookieArena.under', self.config.Task_Dict))
        self.refresh_chance = int(self.config.get('Task.RookieArena.refresh_chance', self.config.Task_Dict))
        self.index = -1

    def run(self):
        self.LINE('Rookie Arena')
        self.go(destination=page_rookie_arena)
        if self.device._hide(free_chance):
            self._finish()
            return
        if self.under:
            self.refresh()
        self.choose_target()
        self._finish()

    def _finish(self):
        self.finish(self.config, 'RookieArena')
        self.INFO('Rookie Arena is finished')

    def choose_target(self):
        timeout = Timer(90).start()
        confirm_timer = Timer(1, count=5).start()
        click_timer = Timer(1.2)

        index = self.target - 1 if self.index == -1 else self.index

        while 1:
            self.device.screenshot()
            if click_timer.reached() and self.device.appear_then_click(save_formation):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(free_chance, index=index):
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

    def refresh(self):
        import cv2

        timeout = Timer(30).start()
        confirm_timer = Timer(0, count=self.refresh_chance).start()
        click_timer = Timer(1.2)

        lcs = self.device.appear(own_power_sign, _result=ImgResult.ALL_RESULT)
        for index, i in enumerate(lcs):
            left, right, top, bottom = i['left'], i['right'], i['top'], i['bottom']
            left += 20
            right += 72
            top -= 5
            bottom += 2

            own_power_area = self.device.image[top:bottom, left:right]

            # img = resize(own_power_area, fx=1.2, fy=1, interpolation=cv2.INTER_NEAREST)
            # self.own_power = int(self.device._ocr(img, line=True))

            img = resize(own_power_area, fx=1.6, fy=0.6, interpolation=cv2.INTER_NEAREST)
            self.own_power = int(self.device._ocr(img, _result=OcrResult.TEXT))

            break

        self.INFO(f'rest chance: {self.refresh_chance}')

        while 1:
            self.device.screenshot()

            lcs = self.device.appear(power_sign, _result=ImgResult.ALL_RESULT)
            for index, i in enumerate(lcs):
                left, right, top, bottom = i['left'], i['right'], i['top'], i['bottom']
                left += 20
                right += 72
                top -= 5
                bottom += 2

                _img = self.device.image[top:bottom, left:right]
                img = resize(_img, fx=1.6, fy=0.6, interpolation=cv2.INTER_NEAREST)
                power = int(self.device._ocr(img, _result=OcrResult.TEXT))

                if self.own_power - power >= self.under:
                    self.INFO(f'own power: {self.own_power}')
                    self.INFO(f'target power: {power}')
                    self.INFO(f'target index: {index + 1}')
                    self.index = index
                    return

            if click_timer.reached() and self.device.appear_then_click(refresh):
                self.refresh_chance -= 1
                self.INFO(f'rest chance: {self.refresh_chance}')
                self.device.sleep(2)
                timeout.reset()
                click_timer.reset()

            if not self.refresh_chance:
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
