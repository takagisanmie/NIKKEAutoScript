from module.base.timer import Timer
from module.base.utils import point2str, _area_offset, crop
from module.logger import logger
from module.mission_pass.assets import *
from module.ui.assets import MAIN_GOTO_PASS, MAIN_CHECK
from module.ui.page import page_main
from module.ui.ui import UI


class MissionPass(UI):
    def receive(self, button, skip_first_screenshot=True):
        confirm_timer = Timer(2, count=2).start()
        _confirm_timer = Timer(1, count=2).start()
        click_timer = Timer(0.3)
        flag = True
        interval = 0
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() \
                    and self.appear(COMPLETED_CHECK, offset=(5, 5), interval=interval, threshold=0.9, static=False) \
                    and COMPLETED_CHECK.match_appear_on(self.device.image, 10):
                self.device.click_minitouch(*_area_offset(COMPLETED_CHECK.location, (-80, 10)))
                logger.info(
                    'Click %s @ %s' % (point2str(*_area_offset(COMPLETED_CHECK.location, (-80, 10))), 'COMPLETED')
                )
                interval = 4
                confirm_timer.reset()
                click_timer.reset()
                self.device.sleep(1.27)
                self.device.click_minitouch(360, 1190)
                continue

            if click_timer.reached() and self.appear(RANK_UP_CHECK, offset=5, interval=1, static=False):
                self.device.click_minitouch(1, 1)
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(PASS_CHECK, offset=5, static=False) \
                    and confirm_timer.reached() \
                    and not self.appear(COMPLETED_CHECK, offset=(5, 5), threshold=0.9, static=False):
                flag = False
                self.device.click_minitouch(1, 1)
                continue

            if flag and click_timer.reached() and self.appear_then_click(button, offset=5, interval=1.2):
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not flag and self.appear(MAIN_CHECK, offset=5, interval=0.3) and _confirm_timer.reached():
                break

    def confirm_transformation(self):
        confirm_timer = Timer(0.6, count=1).start()
        while 1:
            self.device.screenshot()
            if self.appear(CHANGE, offset=5, threshold=0.9, static=False) and confirm_timer.reached():
                break

    def run(self):
        self.ui_ensure(page_main)
        skip_first_screenshot = True
        click_timer = Timer(0.3)

        visited_count = 0
        mp_list = []

        if self.appear(CHANGE, offset=5, threshold=0.9, static=False):
            self.config.PASS_LIMIT = 2
        else:
            self.config.PASS_LIMIT = 1

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.config.PASS_LIMIT == 2 \
                    and click_timer.reached() \
                    and self.appear_then_click(CHANGE, offset=5, threshold=0.9, static=False):

                area = _area_offset(CHANGE.area, (10, -40, 240, 0))
                self.confirm_transformation()
                mp = Button(area, None, button=area)
                mp._match_init = True
                mp.image = crop(self.device.image, area)

                if len(mp_list) == 0 and DOT.match(mp.image, offset=5, static=False):
                    mp_list.append(mp)
                    continue

                for i in mp_list:
                    if not i.match(mp.image, threshold=0.8, static=False):
                        if DOT.match(mp.image, offset=5, static=False):
                            mp_list.append(mp)

                visited_count += 1
                if len(mp_list) == self.config.PASS_LIMIT or visited_count == self.config.PASS_LIMIT:
                    break

                click_timer.reset()

            elif self.config.PASS_LIMIT == 1 \
                    and click_timer.reached() \
                    and self.appear(MAIN_GOTO_PASS, offset=5, threshold=0.9, static=False):

                area = _area_offset(MAIN_GOTO_PASS.area, (10, -40, 100, 0))
                mp = Button(area, None, button=area)
                mp._match_init = True
                mp.image = crop(self.device.image, area)

                if DOT.match(mp.image, offset=5, static=False):
                    mp_list.append(mp)
                break

        logger.attr('PENDING MISSION PASS', len(mp_list))
        if len(mp_list):
            while 1:
                self.device.screenshot()
                if click_timer.reached() and self.appear(mp_list[0], offset=5):
                    self.receive(mp_list[0])
                    mp_list.remove(mp_list[0])
                    logger.attr('PENDING MISSION PASS', len(mp_list))
                    if not len(mp_list):
                        break

                if click_timer.reached() and self.appear_then_click(CHANGE, offset=5):
                    click_timer.reset()
                    self.confirm_transformation()
                    continue
        self.config.task_delay(server_update=True)
