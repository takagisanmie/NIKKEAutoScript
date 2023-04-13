from module.base.base import ModuleBase
from module.exception import GameStuckError, GameServerUnderMaintenance
from module.handler.assets import *


class InfoHandler(ModuleBase):
    def handle_paid_gift(self):
        if self.appear(PAID_GIFT_CHECK, offset=(30, 30), interval=3):
            if self.appear_then_click(CONFRIM_B, offset=(30, 30), interval=3, static=False):
                return True

            elif self.appear_then_click_text('点击关闭画面', interval=3):
                return True

        return False

    def handle_login_reward(self):
        if self.appear_then_click(DAILY_LOGIN_REWARD, offset=(30, 30), interval=3, static=False):
            return True

        # Daily Login, Memories Spring, Monthly Card, etc.
        if self.appear_then_click_text('领取奖励', interval=3):
            return True

        '''
            出现登录奖励时，点击没有被覆盖的位置 
            Daily Login, Memories Spring, etc.
        '''
        if self.appear_text('根据累积登入天数', interval=3):
            self.device.click_minitouch(20, 600)
            return True

        return False

    def handle_server(self):
        if self.appear(SERVER_CHECK, offset=(30, 30), interval=3) \
                and self.appear_then_click(CONFRIM_A, offset=(30, 30), interval=3, static=False):
            return True

    def handle_download(self):
        if self.appear(DOWNLOAD_CHECK, offset=(30, 30), interval=3) \
                and self.appear_then_click(CONFRIM_A, offset=(30, 30), interval=3, static=False):
            return True

    def handle_system_error(self):
        if self.appear(SYSTEM_ERROR_CHECK, offset=(30, 30), interval=3):
            raise GameStuckError('detected system error')

    def handle_system_maintenance(self):
        if self.appear(SYSTEM_MAINTENANCE_CHECK, offset=(30, 30), interval=3):
            raise GameServerUnderMaintenance('Server is currently under maintenance')
