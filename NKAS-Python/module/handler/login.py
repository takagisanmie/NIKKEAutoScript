from common.enum.enum import *
from common.exception import Timeout
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from module.handler.login_assets import *


class LoginHandler(UI):
    def handle_app_login(self):
        timeout = Timer(180).start()
        click_timer = Timer(0.5)
        confirm_timer = Timer(1, count=4).start()

        self.where()
        if UI.current_page is not None and UI.current_page is not page_login:
            return

        flag = False

        while 1:

            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(login_confrim):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(touch_to_continue):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(notice_close):
                flag = True
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                break

            if click_timer.reached() and self.device.textStrategy('根据累积登入天数', None, OcrResult.TEXT):
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.textStrategy('剩余时间', None, OcrResult.TEXT):
                timeout.reset()
                click_timer.reset()
                continue

            if flag:
                if confirm_timer.reached():
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

            self.device.sleep(3)
            # # 关闭公告
            # if self._appear_then_click(assets.close, AssetResponse.ASSET_HIDE):
            #     continue
            # # 选择服务器
            # # if self.appear_then_click(assets.confirm4, AssetResponse.ASSET_HIDE):
            # #     continue
            # self.device.clickTextLocation('确认', AssetResponse.NONE)
            # self.device.clickTextLocation('碓', AssetResponse.NONE)
            # # 进入游戏
            # if self._appear_then_click(assets.enter_into_menu, AssetResponse.ASSET_HIDE):
            #     self.device.wait(assets.in_menu_announcement_sign)
            #     self.device.click(assets.close6, AssetResponse.ASSET_HIDE)
            #     self.device.sleep(8)
            #     if self.device.textStrategy('根据累积登入天数', None, OcrResult.TEXT, True):
            #         self.device.clickLocation((300, 300), AssetResponse.TEXT_HIDE, '根据累积登入天数')
            #         return
            #     elif self.device.textStrategy('活动期间', None, OcrResult.TEXT, False):
            #         self.device.clickLocation((300, 300), AssetResponse.TEXT_HIDE, '活动期间')
            #         return
            #     elif self.device.textStrategy('剩余时间', None, OcrResult.TEXT, False):
            #         self.device.clickLocation((300, 300), AssetResponse.TEXT_HIDE, '剩余时间')
            #         return

    def app_start(self):
        # TODO 自动启动加速器，以及服务器选择
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
        click_timer = Timer(0.3)

        while 1:
            self.device.screenshot()
            if package not in self.device.u2.app_list_running():
                self.device.app_start(package)

            if click_timer.reached() and self.device.appear_then_click(scene):
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(game):
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear(selected_sign) and self.device.appear_then_click(start):
                timeout.reset()
                click_timer.reset()
                continue

            if self.device.appear(successful_sign):
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

        #     self.device.sleep(0.3)
        #     self.device.screenshot()
        #
        #     if lc := match(self.device.image, _close1, 0.84, ImgResult.LOCATION):
        #         self.device.clickLocation(lc, AssetResponse.NONE)
        #         continue
        #
        #     if self.device.textStrategy('发现新版本', None, OcrResult.TEXT):
        #         self.device.u2.press('back')
        #         continue
        #
        #     if lc := match(self.device.image, scene, 0.84, ImgResult.LOCATION):
        #         self.device.clickLocation(lc, AssetResponse.NONE)
        #         continue
        #
        #     if lc := self.device.textStrategy('电竞宽带', None, OcrResult.LOCATION):
        #         self.device.clickLocation(lc, AssetResponse.NONE)
        #         continue
        #
        #     if lc := self.device.textStrategy('开始加速', None, OcrResult.LOCATION):
        #         self.device.clickLocation(lc, AssetResponse.NONE)
        #         continue
        #
        #     if self.device.textStrategy('预计提速', None, OcrResult.LOCATION):
        #         self.device.u2.press(key='back')
        #         continue
        #         # return False
        #
        #     elif self.device.textStrategy('加速计时', None, OcrResult.LOCATION):
        #         return False
        #
        #     elif self.device.textStrategy('停止加速', None, OcrResult.LOCATION):
        #         return False
        #
        #     elif self.device.textStrategy('开始游戏', None, OcrResult.LOCATION):
        #         return False
        #
        #     elif self.device.textStrategy('正在加速', None, OcrResult.LOCATION):
        #         return False

    # uu
    def start_uu(self):
        package = 'com.netease.uu'

        if package not in self.device.u2.app_list():
            self.ERROR('UU加速器未安装')
            return True

        # if package not in self.device.u2.app_list_running():
        #     self.device.app_start(package)
        #     self.device.wait(_global)
        # else:
        #     return False
        #
        # while 1:
        #     self.device.screenshot()
        #     if lc := self.device.textStrategy('取消', None, OcrResult.LOCATION):
        #         self.device.clickLocation(lc, AssetResponse.NONE)
        #         continue
        #
        #     if lc := match(self.device.image, _global, 0.84, ImgResult.LOCATION):
        #         self.device.clickLocation(lc, AssetResponse.ASSET_HIDE, _global)
        #         if lc := self.device.textStrategy('日服', None, OcrResult.LOCATION):
        #             self.device.clickLocation(lc, AssetResponse.NONE)
        #             continue
        #
        #         if lc := self.device.textStrategy('韩服', None, OcrResult.LOCATION):
        #             self.device.clickLocation(lc, AssetResponse.NONE)
        #             continue
        #
        #         if lc := self.device.textStrategy('国际服', None, OcrResult.LOCATION):
        #             self.device.clickLocation(lc, AssetResponse.NONE)
        #             continue
        #
        #         if lc := self.device.textStrategy('北美', None, OcrResult.LOCATION):
        #             self.device.clickLocation(lc, AssetResponse.NONE)
        #             continue
        #
        #         if lc := self.device.textStrategy('东南亚', None, OcrResult.LOCATION):
        #             self.device.clickLocation(lc, AssetResponse.NONE)
        #             continue
        #
        #     else:
        #         if lc := self.device.textStrategy('胜利女神', None, OcrResult.LOCATION):
        #             self.device.multiClickLocation(lc, 2, AssetResponse.NONE)
        #             self.device.sleep(3)
        #             self.device.screenshot()
        #             if self.device.textStrategy('中国台湾', None, OcrResult.LOCATION, False,
        #                                         resized_shape=(2000, 2000)):
        #                 if lc := self.device.textStrategy('加速', None, OcrResult.LOCATION):
        #                     self.device.clickLocation(lc, AssetResponse.NONE)
        #                     continue
        #
        #     if self.device.textStrategy('加速时长', None, OcrResult.LOCATION):
        #         return False
        #
        #     elif self.device.textStrategy('丢包率', None, OcrResult.LOCATION):
        #         return False
        #
        #     elif self.device.textStrategy('综合提速', None, OcrResult.LOCATION):
        #         return False
        #
        #     elif self.device.textStrategy('延迟', None, OcrResult.LOCATION):
        #         return False

    def isVerticalScreen(self):
        self.device.sleep(3)
        self.device.screenshot()
        h, w, c = self.device.image.shape
        if str(w) == '720' and str(h) == '1280':
            return False
        self.ERROR('请将模拟器设置设置为为720x1280')
        return True
