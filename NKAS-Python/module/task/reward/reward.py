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
        self.device.click(button, AssetResponse.ASSET_SHOW, assets.rewards_page)
        self.device.click(assets.rewards_page, AssetResponse.ASSET_SHOW, assets.in_menu_sign)
