from common.enum.enum import *
from common.exception import Timeout
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from module.handler.login_assets import *


class LoginHandler(UI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = int(self.config.get('Server', self.config.dict))
        self.is_finished = False

    def handle_app_login(self, where=True):
        timeout = Timer(180).start()
        click_timer = Timer(1.2)
        confirm_timer = Timer(1, count=8).start()

        if where:
            self.where()

        self.INFO(f'current page: {UI.current_page.name}')

        if UI.current_page is not None and UI.current_page is not page_login:
            return

        self.LINE('Login')

        while 1:

            self.device.screenshot()

            if self.server == NIKKEServer.JP and self.config.Emulator_JP_PackageName not in self.device.u2.app_list_running():
                self.device.u2.app_start(self.config.Emulator_JP_PackageName)

            elif self.server == NIKKEServer.TW and self.config.Emulator_TW_PackageName not in self.device.u2.app_list_running():
                self.device.u2.app_start(self.config.Emulator_TW_PackageName)

            # 礼包
            if click_timer.reached() and self.device.appear(gift) and self.device.appear_then_click(confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(gift):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            # 在登录页
            if self.device.appear(login_sign):
                timeout.reset()
                confirm_timer.reset()

            # 需要下载
            if self.device.appear(download_sign):
                timeout.reset()
                confirm_timer.reset()

            # 在下载页
            if self.device.textStrategy('正在下载', None, OcrResult.TEXT):
                timeout.reset()
                confirm_timer.reset()
                self.device.sleep(5)
                continue

            if click_timer.reached() and self.device.appear_then_click(confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            # 系统错误
            if click_timer.reached() and self.device.appear(system_error) and self.device.appear_then_click(
                    small_confirm):
                self.device.sleep(10)
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            # 更新NIKKE
            if click_timer.reached() and self.device.appear(download_sign) and self.device.appear_then_click(
                    small_confirm):
                self.device.sleep(10)
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(login_confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(touch_to_continue):
                self.device.sleep(5)
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(notice_close):
                self.device.sleep(5)
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(get_daily_login_reward):
                timeout.reset()
                click_timer.reset()
                continue

            # 月卡
            if click_timer.reached() and self.device.textStrategy('补给品每日奖励', None, OcrResult.TEXT):
                self.device.multiClickLocation((360, 850))
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.textStrategy('根据累积登入天数', None, OcrResult.TEXT):
                self.device.multiClickLocation((20, 600))
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.textStrategy('剩余时间', None, OcrResult.TEXT):
                self.device.multiClickLocation((20, 600))
                timeout.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                self.INFO('login success')
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

            self.device.sleep(1.27)

    def app_start(self):
        # TODO 自动启动加速器
        accelerator = self.config.Simulator_Accelerator
        if accelerator is not None:
            if accelerator == 'UU':
                if self.start_uu():
                    return False

            elif accelerator == 'ACGP':
                pass

            elif accelerator == 'Universal':
                if self.start_universalapp():
                    return False

        if self.device.app_start():
            return False

        if self.isVerticalScreen():
            return False

        self.handle_app_login()
        return True

    # 和家亲
    def start_universalapp(self):
        package = 'com.cmri.universalapp'
        if package not in self.device.u2.app_list():
            self.ERROR('和家亲未安装')
            return True

        if package not in self.device.u2.app_list_running():
            self.device.app_start(package)
        else:
            return False

        timeout = Timer(30).start()
        click_timer = Timer(1.2)

        swipe = True
        swipe_to_right = True

        while 1:
            self.device.screenshot()
            if package not in self.device.u2.app_list_running():
                self.device.app_start(package)

            if click_timer.reached() and self.device.appear(not_found):
                self.device.app_stop(package)
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(scene):
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(game):
                timeout.reset()
                click_timer.reset()
                self.device.sleep(3)
                continue

            if click_timer.reached() and self.device.appear(selected_sign) and (lc := self.device.appear(start)):
                self.device.multiClickLocation(lc, count=3)
                swipe = False
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear(AD):
                self.device.u2.press(key='back')
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(close_grade):
                timeout.reset()
                click_timer.reset()
                continue

            if self.device.appear(successful_sign):
                return

            if self.device.appear(far_right):
                swipe_to_right = False

            if swipe and self.device.textStrategy('手机游戏加速', None, OcrResult.TEXT):
                if swipe_to_right \
                        and click_timer.reached() \
                        and self.device.swipe(340, 540, 100, 540, 0.2):
                    timeout.reset()
                    click_timer.reset()
                    continue
                else:
                    if click_timer.reached() and self.device.swipe(100, 540, 340, 540, 0.2):
                        timeout.reset()
                        click_timer.reset()
                        continue

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    # uu
    def start_uu(self):
        package = 'com.netease.uu'

        if package not in self.device.u2.app_list():
            self.ERROR('UU加速器未安装')
            return True

    def isVerticalScreen(self):
        self.device.sleep(3)
        self.device.screenshot()
        h, w, c = self.device.image.shape
        if str(w) == '720' and str(h) == '1280':
            return False
        self.ERROR('请将模拟器设置设置为为720x1280')
        return True
