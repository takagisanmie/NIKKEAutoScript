import assets
from common.enum.enum import *
from module.ui.page import *
from module.ui.ui import UI


class LoginHandler(UI):
    def handle_app_login(self):
        while 1:
            self.where()
            if UI.current_page is not None and UI.current_page is not page_login and UI.current_page in page_list:
                return True
            self.device.screenshot()
            # 关闭公告
            if self.appear_then_click(assets.close, AssetResponse.ASSET_HIDE):
                continue
            # 选择服务器
            # if self.appear_then_click(assets.confirm4, AssetResponse.ASSET_HIDE):
            #     continue
            self.device.clickTextLocation('确认', AssetResponse.NONE)
            self.device.clickTextLocation('碓', AssetResponse.NONE)
            # 进入游戏
            if self.appear_then_click(assets.enter_into_menu, AssetResponse.ASSET_HIDE):
                self.device.wait(assets.in_menu_announcement_sign)
                self.device.click(assets.close6, AssetResponse.ASSET_HIDE)
                self.device.sleep(8)
                if self.device.textStrategy('根据累积登入天数', None, OcrResult.TEXT, True):
                    self.device.clickLocation((300, 300), AssetResponse.TEXT_HIDE, '根据累积登入天数')
                    return
                elif self.device.textStrategy('活动期间', None, OcrResult.TEXT, False):
                    self.device.clickLocation((300, 300), AssetResponse.TEXT_HIDE, '活动期间')
                    return
                elif self.device.textStrategy('剩余时间', None, OcrResult.TEXT, False):
                    self.device.clickLocation((300, 300), AssetResponse.TEXT_HIDE, '剩余时间')
                    return

    def app_start(self):
        # TODO 自动启动加速器，以及服务器选择
        accelerator = self.config.Simulator_Accelerator
        if accelerator is not None:
            if accelerator == 'UU':
                if self.start_uu():
                    return True

            elif accelerator == 'ACGP':
                pass

            elif accelerator == 'Universal':
                if self.start_universalapp():
                    return True

        if self.device.app_start():
            return True

        if self.isHorizontalScreen():
            return True
        self.handle_app_login()
        return False

    # 和家亲
    def start_universalapp(self):
        from module.tools.match import match
        from module.handler.assets import close1 as _close1, scene
        package = 'com.cmri.universalapp'
        if package not in self.device.u2.app_list():
            self.ERROR('和家亲未安装')
            return True

        if package not in self.device.u2.app_list_running():
            self.device.app_start(package)
        else:
            return False

        while 1:

            self.device.sleep(0.3)
            self.device.screenshot()

            if lc := match(self.device.image, _close1, 0.84, ImgResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue

            if self.device.textStrategy('发现新版本', None, OcrResult.TEXT):
                self.device.u2.press('back')
                continue

            if lc := match(self.device.image, scene, 0.84, ImgResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue

            if lc := self.device.textStrategy('电竞宽带', None, OcrResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue

            if lc := self.device.textStrategy('开始加速', None, OcrResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue

            if self.device.textStrategy('预计提速', None, OcrResult.LOCATION):
                self.device.u2.press(key='back')
                continue
                # return False

            elif self.device.textStrategy('加速计时', None, OcrResult.LOCATION):
                return False

            elif self.device.textStrategy('停止加速', None, OcrResult.LOCATION):
                return False

            elif self.device.textStrategy('开始游戏', None, OcrResult.LOCATION):
                return False

            elif self.device.textStrategy('正在加速', None, OcrResult.LOCATION):
                return False

    # uu
    def start_uu(self):
        from module.tools.match import match
        from module.handler.assets import _global
        package = 'com.netease.uu'

        if package not in self.device.u2.app_list():
            self.ERROR('UU加速器未安装')
            return True

        if package not in self.device.u2.app_list_running():
            self.device.app_start(package)
            self.device.wait(_global)
        else:
            return False

        while 1:
            self.device.screenshot()
            if lc := self.device.textStrategy('取消', None, OcrResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue

            if lc := match(self.device.image, _global, 0.84, ImgResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.ASSET_HIDE, _global)
                if lc := self.device.textStrategy('日服', None, OcrResult.LOCATION):
                    self.device.clickLocation(lc, AssetResponse.NONE)
                    continue

                if lc := self.device.textStrategy('韩服', None, OcrResult.LOCATION):
                    self.device.clickLocation(lc, AssetResponse.NONE)
                    continue

                if lc := self.device.textStrategy('国际服', None, OcrResult.LOCATION):
                    self.device.clickLocation(lc, AssetResponse.NONE)
                    continue

                if lc := self.device.textStrategy('北美', None, OcrResult.LOCATION):
                    self.device.clickLocation(lc, AssetResponse.NONE)
                    continue

                if lc := self.device.textStrategy('东南亚', None, OcrResult.LOCATION):
                    self.device.clickLocation(lc, AssetResponse.NONE)
                    continue

            else:
                if lc := self.device.textStrategy('胜利女神', None, OcrResult.LOCATION):
                    self.device.multiClickLocation(lc, 2, AssetResponse.NONE)
                    self.device.sleep(3)
                    self.device.screenshot()
                    if self.device.textStrategy('中国台湾', None, OcrResult.LOCATION, False,
                                                resized_shape=(2000, 2000)):
                        if lc := self.device.textStrategy('加速', None, OcrResult.LOCATION):
                            self.device.clickLocation(lc, AssetResponse.NONE)
                            continue

            if self.device.textStrategy('加速时长', None, OcrResult.LOCATION):
                return False

            elif self.device.textStrategy('丢包率', None, OcrResult.LOCATION):
                return False

            elif self.device.textStrategy('综合提速', None, OcrResult.LOCATION):
                return False

            elif self.device.textStrategy('延迟', None, OcrResult.LOCATION):
                return False

    def isHorizontalScreen(self):
        self.device.sleep(3)
        self.device.screenshot()
        h, w, c = self.device.image.shape
        if str(w) == '1920' and str(h) == '1080':
            return False
        self.ERROR('请将模拟器设置为强制横屏模式')
        return True
