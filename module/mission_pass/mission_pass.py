from module.base.timer import Timer
from module.base.utils import mask_area, point2str, _area_offset
from module.logger import logger
from module.mission_pass.assets import *
from module.ui.assets import PASS_CHECK
from module.ui.page import page_pass
from module.ui.ui import UI


class MissionPass(UI):
    def receive(self, skip_first_screenshot=True):
        confirm_timer = Timer(3, count=3).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()
                self.device.image = mask_area(self.device.image, COMPLETED_CHECK.button)

            if click_timer.reached() and self.appear(COMPLETED_CHECK, offset=(5, 5), interval=2,
                                                     threshold=0.8, static=False):
                self.device.click_minitouch(*_area_offset(COMPLETED_CHECK.location, (-80, 10)))
                logger.info(
                    'Click %s @ %s' % (point2str(*_area_offset(COMPLETED_CHECK.location, (-80, 10))), 'COMPLETED')
                )
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and RECEIVE.appear_on(self.device.image):
                self.device.click(RECEIVE)
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear(RANK_UP_CHECK, offset=(10, 10), static=False):
                self.device.click_minitouch(360, 870)
                logger.info(
                    'Click %s @ %s' % (point2str(360, 870), 'RANK_UP')
                )
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(PASS_CHECK) and confirm_timer.reached():
                self.device.screenshot()
                if self.appear(COMPLETED_CHECK, offset=(5, 5), threshold=0.8, static=False):
                    skip_first_screenshot = True
                    continue
                break

    def temporary(self, button, skip_first_screenshot=True):
        click_timer = Timer(0.3)
        confirm_timer = Timer(1, count=2).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(button, offset=(30, 30),
                                                                interval=0.3, static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                break

    def run(self):
        # ----
        self.ui_ensure(page_pass)
        # ----
        # self.ui_ensure(page_main)
        # self.temporary(MAIN_GOTO_PASS)
        # ----
        self.receive()
        self.config.task_delay(server_update=True)
