from module.base.base import ModuleBase
from module.exception import GameStuckError, GameServerUnderMaintenance
from module.handler.assets import *
from module.logger import logger
from module.ui.page import SKIP, TOUCH_TO_CONTINUE


class InfoHandler(ModuleBase):
    def handle_paid_gift(self, interval=1):
        if self.appear(PAID_GIFT_CHECK, offset=(30, 30), interval=interval, static=False):
            if self.appear_text_then_click('点击关闭画面', interval=interval):
                return True

        elif self.appear(PAID_GIFT_CONFIRM_CHECK, offset=(30, 30), interval=interval, static=False):
            if self.appear_then_click(CONFRIM_B, offset=(30, 30), interval=interval, static=False):
                return True

        return False

    def handle_login_reward(self):
        if self.appear_then_click(DAILY_LOGIN_REWARD, offset=(30, 30), interval=2, static=False, threshold=0.6):
            self.device.sleep(2)
            return True

        if self.appear_then_click(DAILY_LOGIN_REWARD_2, offset=(30, 30), interval=2, static=False):
            self.device.sleep(2)
            return True

        # Daily Login, Memories Spring, Monthly Card, etc.
        if self.appear_text_then_click('_领取奖励', interval=1):
            self.device.sleep(2)
            return True

        if self.appear_text_then_click('_全部领取', interval=6):
            self.device.sleep(1)
            return True

        '''
            出现登录奖励时，点击没有被覆盖的位置 
            Daily Login, Memories Spring, etc.
        '''
        # 420:550, 230:700
        if self._appear_text_then_click('根据累积登入天数', (20, 600), 'CLOSE_DAILY_LOGIN_A', interval=5,
                                        area=(230, 420, 700, 550)):
            self.device.sleep(3)
            return True

        if self._appear_text_then_click('根据累积登入天数', (20, 600), 'CLOSE_DAILY_LOGIN_B', interval=5,
                                        area=(165, 255, 560, 290)):
            self.device.sleep(3)
            return True

        if self._appear_text_then_click('根据累积登入天数', (20, 600), 'CLOSE_DAILY_LOGIN_C', interval=5,
                                        area=(165, 300, 570, 340)):
            self.device.sleep(3)
            return True

        if self.appear_then_click(CLOSE_DAILY_LOGIN_C, offset=(30, 30), interval=5, static=False):
            self.device.sleep(2)
            return True

        return False

    def handle_reward(self, interval=5):
        if self.appear_then_click(REWARD, offset=(30, 30), interval=interval, static=False):
            return True

    def handle_level_up(self, interval=3):
        if self.appear(LEVEL_UP_CHECK, offset=(30, 30), interval=interval):
            self.device.click_minitouch(360, 920)
            logger.info('Click (360, 920) @ LEVEL_UP')
            return True

    def handle_server(self):
        if self.appear(SERVER_CHECK, offset=(30, 30), interval=3, static=False) \
                and self.appear_then_click(CONFRIM_A, offset=(30, 30), interval=3, static=False):
            return True

    def handle_popup(self):
        if self.appear(POPUP_CHECK, offset=(30, 30), interval=3, static=False) \
                and self.appear_then_click(ANNOUNCEMENT, offset=(30, 30), interval=3, threshold=0.74, static=False):
            return True

    def handle_announcement(self):
        if self.appear(ANNOUNCEMENT_CHECK, offset=(30, 30), interval=3, threshold=0.74, static=False) \
                and self.appear_then_click(ANNOUNCEMENT, offset=(30, 30), interval=3, threshold=0.74, static=False):
            return True

    def handle_download(self):
        if self.appear(DOWNLOAD_CHECK, offset=(30, 30), interval=3, static=False) \
                and self.appear_then_click(CONFRIM_A, offset=(30, 30), interval=3, static=False):
            return True

    def handle_system_error(self):
        if self.appear(SYSTEM_ERROR_CHECK, offset=(30, 30), interval=3, static=False):
            raise GameStuckError('detected system error')

    def handle_system_maintenance(self):
        if self.appear(SYSTEM_MAINTENANCE_CHECK, offset=(30, 30), interval=3, static=False):
            raise GameServerUnderMaintenance('Server is currently under maintenance')

    def handle_event(self, interval=3):
        if self.appear_then_click(SKIP, offset=(5, 5), static=False, interval=interval):
            return True
        elif self.appear_then_click(TOUCH_TO_CONTINUE, offset=(5, 5), static=False, interval=interval):
            self.device.click_minitouch(360, 720)
            return True

    def handle_login(self):
        if self.appear(LOGIN_CHECK, offset=(30, 30), interval=5) or self.appear(LOGIN_CHECK_B, offset=(30, 30),
                                                                                interval=5):
            self.device.click(LOGIN_CHECK)
            logger.info('Login success')
