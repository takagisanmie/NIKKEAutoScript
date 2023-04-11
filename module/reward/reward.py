from module.base.timer import Timer
from module.logger import logger
from module.reward.assets import *
from module.ui.page import *
from module.ui.ui import UI


class Reward(UI):
    def receive_reward(self, skip_first_screenshot=True):
        logger.hr('Reward receive')
        confirm_timer = Timer(2, count=3).start()
        # Set click interval to 0.3, because game can't respond that fast.
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(RECEIVE, interval=3):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(REWARD, interval=1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            # End
            if confirm_timer.reached():
                break

        logger.info('Defence Reward receive end')
        return True

    def run(self):
        self.ui_ensure(page_reward)
        self.receive_reward()
        self.config.task_delay(success=True)
