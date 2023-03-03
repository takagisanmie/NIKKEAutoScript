import assets
from common.enum.enum import *
from module.base.task import Task
from module.ui.page import *
from module.ui.ui import UI


class FreeStore(UI, Task):
    def run(self):
        self.LINE('Free Store')
        self.go(destination=page_free_store)
        if self.device.isVisible(assets.in_free_store_free_goods, 0.95):
            self.buy()
        else:
            self.INFO('store is at present has no free product')
        self.device.clickLocation((350, 490), AssetResponse.ASSET_SHOW, assets.in_free_store_free_reset_confirm)
        if self.device.isVisible(assets.in_free_store_free_reset, 0.95):
            self.device.click(assets.in_free_store_free_reset_confirm, AssetResponse.ASSET_HIDE)
            self.INFO('reset store')
            self.buy()
        else:
            self.device.click(assets.in_free_store_free_reset_cancel, AssetResponse.ASSET_HIDE)

        self.device.click(assets.home, AssetResponse.ASSET_HIDE)
        self.finish(self.config, 'FreeStore')
        self.INFO('Free Store is finished')

    def buy(self):
        self.device.click(assets.in_free_store_free_goods, AssetResponse.ASSET_SHOW, assets.in_free_store_confrim)
        self.device.click(assets.in_free_store_confrim, AssetResponse.ASSET_SHOW, assets.rewards_page)
        self.device.click(assets.rewards_page, AssetResponse.ASSET_HIDE)
