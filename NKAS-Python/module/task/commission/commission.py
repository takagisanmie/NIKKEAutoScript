import assets
from common.enum.enum import *
from module.base.task import Task
from module.ui.page import *
from module.ui.ui import UI


class Commission(UI, Task):
    def run(self):
        self.LINE('Commission')
        self.go(destination=page_outpost_child_commission)
        # 此处会卡顿，游戏问题
        self.device.sleep(8)
        self.device.screenshot()
        if self.device.isVisible(assets.in_outpost_commission_dispatch_button):
            self.device.click(assets.in_outpost_commission_dispatch_button, AssetResponse.ASSET_HIDE)
            self.device.click(assets.in_outpost_commission_dispatch_confirm_button, AssetResponse.ASSET_HIDE)
        elif self.device.isVisible(assets.get_reward2):
            self.device.click(assets.get_reward2, AssetResponse.ASSET_SHOW, assets.rewards_page)
            self.device.click(assets.rewards_page, AssetResponse.ASSET_SHOW, assets.in_outpost_commission_sign)

        self.device.click(page_outpost_child_commission.closeButton, AssetResponse.ASSET_HIDE)
        self.device.click(assets.home, AssetResponse.ASSET_HIDE)
        self.finish(self.config, 'Commission')
        self.INFO('Commission is finished')
