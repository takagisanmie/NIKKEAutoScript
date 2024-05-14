from module.base.timer import Timer
from module.base.utils import point2str, _area_offset, crop
from module.logger import logger
from module.mission_pass.assets import *
from module.ui.assets import PASS_CHECK, MAIN_GOTO_PASS, MAIN_CHECK
from module.ui.page import page_main
from module.ui.ui import UI


class MissionPass(UI):
    def receive(self, button, skip_first_screenshot=True):
        confirm_timer = Timer(1, count=2).start()
        _confirm_timer = Timer(1, count=2).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() \
                    and self.appear(COMPLETED_CHECK, offset=(5, 5), interval=2, threshold=0.9, static=False) \
                    and COMPLETED_CHECK.match_appear_on(self.device.image, 10):
                self.device.click_minitouch(*_area_offset(COMPLETED_CHECK.location, (-80, 10)))
                logger.info(
                    'Click %s @ %s' % (point2str(*_area_offset(COMPLETED_CHECK.location, (-80, 10))), 'COMPLETED')
                )
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(button, offset=5, interval=1):
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

            if self.appear(PASS_CHECK, offset=5) \
                    and confirm_timer.reached() \
                    and not self.appear(COMPLETED_CHECK, offset=(5, 5), threshold=0.9, static=False):
                self.device.screenshot()
                self.device.click_minitouch(1, 1)
                continue

            if self.appear(MAIN_CHECK, offset=5) and _confirm_timer.reached():
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
                x1, y1, x2, y2 = map(int, CHANGE.area)

                def confirm_transformation():
                    confirm_timer = Timer(0.6, count=1).start()
                    while 1:
                        self.device.screenshot()
                        if self.appear(CHANGE, offset=5, threshold=0.96, static=False) and confirm_timer.reached():
                            break

                confirm_transformation()

                mp = Button((x1 + 10, y1 - 40, x2 + 240, y2), None,
                            button=(x1 + 10, y1 - 40, x2 + 240, y2))
                mp._match_init = True
                mp.image = crop(self.device.image, (x1 + 10, y1 - 40, x2 + 240, y2))
                visited_count += 1

                if len(mp_list) == 0 and DOT.match(mp.image, offset=5, static=False):
                    mp_list.append(mp)
                    continue

                for i in mp_list:
                    if not i.match(mp.image, threshold=0.9, static=False):
                        if DOT.match(mp.image, offset=5, static=False):
                            mp_list.append(mp)

                if len(mp_list) == self.config.PASS_LIMIT or visited_count == self.config.PASS_LIMIT:
                    break

                click_timer.reset()

            elif self.config.PASS_LIMIT == 1 \
                    and click_timer.reached() \
                    and self.appear(MAIN_GOTO_PASS, offset=5, threshold=0.9, static=False):
                x1, y1, x2, y2 = map(int, MAIN_GOTO_PASS.area)

                mp = Button((x1 + 10, y1 - 40, x2 + 80, y2), None,
                            button=(x1 + 10, y1 - 40, x2 + 80, y2))
                mp._match_init = True
                mp.image = crop(self.device.image, (x1 + 10, y1 - 40, x2 + 80, y2))

                if DOT.match(mp.image, offset=5, static=False):
                    mp_list.append(mp)
                break

        for i in mp_list:
            while 1:
                self.device.screenshot()
                if click_timer.reached() and self.appear_then_click(i, offset=5):
                    self.receive(i)
                    mp_list.remove(i)
                    break

                if click_timer.reached() and self.appear_then_click(CHANGE, offset=5):
                    click_timer.reset()
                    continue

            if not len(mp_list):
                break
        self.config.task_delay(server_update=True)
