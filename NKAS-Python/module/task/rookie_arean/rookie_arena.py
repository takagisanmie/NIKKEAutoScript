from common.enum.enum import *
from module.base.task import Task
from module.ui.page import *
from module.ui.ui import UI


class RookieArena(UI, Task):
    def run(self):
        self.LINE('Rookie Arena')
        self.go(destination=page_arean_Rookie)
        while 1:
            if self.device.isVisible(assets.in_arena_Rookie_disabled_start_button, 0.92):
                self.INFO('Rookie Arena has no free chance')
                break
            self.device.click(assets.in_arena_Rookie_start_button, AssetResponse.ASSET_SHOW, assets.into_battle)
            self.device.click(assets.into_battle, AssetResponse.ASSET_HIDE)
            self.device.wait(assets.end_battle)
            self.device.clickLocation((300, 300), AssetResponse.ASSET_SHOW, assets.in_arena_Rookie_sign)

        self.device.click(assets.home, AssetResponse.ASSET_HIDE)
        self.finish(self.config, 'RookieArena')
        self.INFO('Rookie Arena is finished')
