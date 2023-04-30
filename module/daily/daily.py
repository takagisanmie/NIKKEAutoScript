from module.base.timer import Timer
from module.base.utils import mask_area
from module.common.enum.webui import ICON
from module.daily.assets import *
from module.logger import logger
from module.ui.assets import DAILY_CHECK
from module.ui.page import page_daily
from module.ui.ui import UI


class Daily(UI):
    def receive(self, skip_first_screenshot=True):
        logger.hr('Reward receive', 2)
        confirm_timer = Timer(6, count=2).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()
                self.device.image = mask_area(self.device.image, COMPLETED_CHECK.button)

            if click_timer.reached() and self.appear_then_click(COMPLETED_CHECK, offset=(5, 5), interval=4,
                                                                threshold=0.8, static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(RECEIVE, offset=(5, 5), interval=2,
                                                                static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(DAILY_CHECK, offset=(10, 10)) and confirm_timer.reached():
                break

    def toast(self):
        print(ICON.Helm_Circle)
        from winotify import Notification
        toast = Notification(app_id="NKAS",
                             title="NKAS",
                             msg="任务已全部完成！",
                             icon=ICON.Helm_Circle,
                             duration='long')

        toast.show()

    def run(self):
        self.ui_ensure(page_daily)
        self.receive()
        if self.config.Notification_WhenDailyTaskCompleted:
            self.toast()
        self.config.task_delay(server_update=True)
