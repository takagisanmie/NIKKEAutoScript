from module.base.timer import Timer
from module.exception import RequestHumanTakeover, GameTooManyClickError, GameStuckError
from module.handler.assets import *
from module.logger import logger
from module.ui.assets import *
from module.ui.ui import UI


class LoginHandler(UI):
    def _handle_app_login(self):
        """
        Pages:
            in: Any page
            out: page_main
        """
        logger.hr('App login')

        confirm_timer = Timer(5, count=6).start()
        orientation_timer = Timer(10)
        login_success = False

        while 1:
            # 检查设备方向
            if not login_success and orientation_timer.reached():
                self.device.get_orientation()
                orientation_timer.reset()

            self.device.screenshot()

            # 当 MAIN_CHECK 累计出现5次，并且保持在6秒以上
            if self.appear(MAIN_CHECK, offset=(30, 30)):
                if confirm_timer.reached():
                    logger.info('Login to main confirm')
                    break
            else:
                confirm_timer.reset()

            if self.appear_text('正在下载'):
                self.device.stuck_record_clear()
                self.device.click_record_clear()
                self.device.sleep(10)
                continue

            # TOUCH TO CONTINUE
            if self.appear(LOGIN_CHECK, offset=(30, 30), interval=5) and LOGIN_CHECK.match_appear_on(self.device.image):
                self.device.click(LOGIN_CHECK)
                if not login_success:
                    logger.info('Login success')
                    login_success = True

            # 公告
            if self.appear_then_click(ANNOUNCEMENT, offset=(30, 30), interval=5, static=False):
                continue

            # ———— REWARD ————
            if self.appear_then_click(REWARD, offset=(30, 30), interval=5, static=False):
                continue

            # 确认
            if self.appear_then_click(CONFRIM_A, offset=(30, 30), interval=5, static=False):
                continue

            # Daily Login, Memories Spring, Monthly Card  etc.
            if login_success and self.appear_then_click_text('领取奖励', interval=5):
                continue

            # 礼包
            if login_success and self.appear_then_click_text('点击关闭画面', interval=5):
                continue

            # 出现登录奖励时，点击没有被覆盖的位置
            if login_success and (
                    self.appear_text('根据累积登入天数', interval=5) or self.appear_text('剩余时间', interval=5)):
                self.device.click_minitouch(20, 600)
                continue

    def handle_app_login(self) -> bool:
        """
            Returns:
                bool: 是否登录成功

            Raises:
                RequestHumanTakeover: 当登录失败次数大于3次时
        """
        for _ in range(3):
            self.device.stuck_record_clear()
            self.device.click_record_clear()
            try:
                self._handle_app_login()
                return True
            except (GameTooManyClickError, GameStuckError) as e:
                logger.warning(e)
                self.device.app_stop()
                self.device.app_start()
                continue

        logger.critical('Login failed more than 3')
        logger.critical('NIKKE server may be under maintenance, or you may lost network connection')
        raise RequestHumanTakeover

    def app_start(self):
        logger.hr('App start')
        self.device.app_start()
        self.handle_app_login()

    def app_stop(self):
        logger.hr('App stop')
        self.device.app_stop()
