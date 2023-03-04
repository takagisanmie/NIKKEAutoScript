from common.enum.enum import *
from module.base.task import Task
from module.ui.page import *
from module.ui.ui import UI


class Reward(UI, Task):
    def run(self):
        self.LINE('Reward')
        self.go(destination=page_main_child_reward_box)
        self.getReward(assets.get_reward)
        self.finish(self.config, 'Reward')
        self.INFO('Reward is finished')

    def getReward(self, button):
        from module.tools.match import match
        self.device.click(button, AssetResponse.ASSET_HIDE)
        self.device.sleep(1)
        while 1:
            self.device.screenshot()
            if lc := self.device.textStrategy('确', None, OcrResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue

            elif lc := self.device.textStrategy('确', None, OcrResult.LOCATION, False,
                                                resized_shape=(2000, 2000)):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue

            if lc := self.device.textStrategy('点击关闭', None, OcrResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue
            elif lc := self.device.textStrategy('点击关闭', None, OcrResult.LOCATION, False,
                                                resized_shape=(2000, 2000)):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue

            if lc := match(self.device.image, assets.rewards_page, 0.84, ImgResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.NONE)
                continue

            if self.device.isVisible(assets.in_menu_sign, 0.92):
                return
