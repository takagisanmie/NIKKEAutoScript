import assets
from common.enum.enum import *
from module.base.task import Task
from module.ui.page import *
from module.ui.ui import UI


class FriendshipPoint(UI, Task):
    def run(self):
        self.LINE('Friendship Point')
        self.go(destination=page_main_child_friends)
        self.device.sleep(6)
        self.device.screenshot()
        if self.appear_then_click(assets.in_friends_give, AssetResponse.ASSET_SHOW, False, assets.confirm3):
            self.device.click(assets.confirm3, AssetResponse.ASSET_HIDE)

        self.finish(self.config, 'FriendshipPoint')
        self.INFO('Friendship Point is finished')
