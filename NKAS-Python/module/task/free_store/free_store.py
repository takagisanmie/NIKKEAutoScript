from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from module.task.free_store.free_store_assets import *


class FreeStore(UI, Task):
    def run(self):
        self.LINE('Free Store')
        self.go(destination=page_free_store)
        self.buy()
        self.device.appear_then_click(home)
        self.finish(self.config, 'FreeStore')
        self.INFO('Free Store is finished')

    def buy(self):
        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        _refresh = True

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(free_sale):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear(free_sale_2) and self.device.appear_then_click(
                    confirm,
                    img_template=bottom):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if _refresh and click_timer.reached() and self.device.appear_then_click(refresh):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.appear(refresh_sign):
                _refresh = False

            if click_timer.reached() \
                    and self.device.appear(refresh_sign) \
                    and self.device.appear(free_refresh) \
                    and self.device.appear_then_click(confirm, img_template=middle):
                self.INFO('refresh store')
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(cancel_2):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
