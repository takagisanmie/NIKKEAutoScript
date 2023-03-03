import assets
from common.enum.enum import *
from module.base.task import Task
from module.ui.page import *
from module.ui.ui import UI


class Destroy(UI, Task):
    def run(self):
        self.LINE('Destroy')
        self.go(destination=page_main_child_reward_box_child_destroy)
        if self.device.isVisible(assets.in_menu_reward_box_destroy, 0.95):
            self.device.click(assets.in_menu_reward_box_destroy, AssetResponse.ASSET_HIDE)
            self.device.click(assets.rewards_page, AssetResponse.ASSET_HIDE)
        else:
            self.INFO('Destroy has no free chance')
        self.finish(self.config, 'Destroy')
        self.INFO('Destroy is finished')
