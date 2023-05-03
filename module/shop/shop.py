from module.base.timer import Timer
from module.handler.assets import CONFRIM_B
from module.logger import logger
from module.shop.assets import *
from module.ui.page import page_shop
from module.ui.ui import UI


class Shop(UI):
    def general_shop(self, skip_first_screenshot=True):
        confirm_timer = Timer(5, count=2).start()
        click_timer = Timer(1.8)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(GRATIS, offset=(5, 5), interval=5, static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(BUY, offset=(5, 5), interval=5, static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(interval=0.3):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(GENERAL_SHOP_CHECK, offset=(5, 5)) and confirm_timer.reached():
                break

    def ensure_fresh(self, skip_first_screenshot=True):
        confirm_timer = Timer(5, count=2).start()
        click_timer = Timer(1.8)
        flag = False
        already_checked = False
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if not already_checked and click_timer.reached() and self.appear_then_click(REFRESH, offset=(5, 5),
                                                                                        interval=3, static=False):
                click_timer.reset()
                continue

            if click_timer.reached() \
                    and self.appear(GRATIS_REFRESH, offset=(5, 5), threshold=0.96, static=False) \
                    and self.appear_then_click(CONFRIM_B, offset=(5, 5), static=False):
                flag = True
                already_checked = True
                click_timer.reset()
                continue

            elif click_timer.reached() and self.appear(CONFRIM_B, offset=(5, 5), static=False):
                already_checked = True

            if not flag and already_checked and click_timer.reached() and self.appear_then_click(CANCEL, offset=(5, 5),
                                                                                                 interval=3,
                                                                                                 static=False):
                click_timer.reset()
                continue

            if already_checked and confirm_timer.reached() and self.appear(GENERAL_SHOP_CHECK, offset=(5, 5)):
                break

        return flag

    def ensure_into_shop(self, button, check, skip_first_screenshot=True):
        logger.hr(f"{check.name.split('_')[:1][0]} SHOP", 2)
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(button, offset=(5, 5), interval=5):
                click_timer.reset()
                continue

            if self.appear(check, offset=(5, 5)):
                break

    def run(self):
        self.ui_ensure(page_shop)
        if self.config.GeneralShop_enable:
            self.ensure_into_shop(GOTO_GENERAL_SHOP, GENERAL_SHOP_CHECK)
            self.general_shop()
            if self.ensure_fresh():
                self.general_shop()

        self.config.task_delay(server_update=True)
