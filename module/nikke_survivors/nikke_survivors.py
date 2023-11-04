import datetime
import time

from module.base.timer import Timer
from module.daily.assets import SW, LU_CHECK
from module.logger import logger
from module.ui.ui import UI


class NikkeSurvivors(UI):

    def run(self):
        click_timer = Timer(0.2)
        confirm_timer = Timer(5, count=5).start()
        skip_first_screenshot = True
        start_time = time.time()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if confirm_timer.reached():
                total_time = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp((time.time() - start_time)),
                                                        "%H:%M:%S")
                logger.info('挂机时间: %s' % total_time)
                confirm_timer.reset()

            if click_timer.reached() and self.appear(SW):
                self.device.drag_minitouch((360, 640), (500, 640))
                self.device.stuck_record_clear()
                self.device.click_record_clear()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear(LU_CHECK):
                self.device.click_minitouch(360, 640)
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_text_then_click('START', interval=3):
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_text_then_click('确认', interval=3):
                click_timer.reset()
                continue

            if click_timer.reached() and self._appear_text_then_click('_白雪公主', (360, 1200), '白雪公主', interval=3):
                click_timer.reset()
                continue

        self.config.task_delay(server_update=True)
