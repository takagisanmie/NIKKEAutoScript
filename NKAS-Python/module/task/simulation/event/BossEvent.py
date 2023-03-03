import assets
from common.enum.enum import *
from module.task.simulation.event.BattleEvent import BattleEvent


class BossEvent(BattleEvent):
    def run(self):
        print('BossEvent')
        self.INFO('start BossEvent')
        self.initBattle()
        while 1:
            self.device.screenshot()
            print('area:' + self.parent.currentArea)
            if self.parent.currentArea == '1' or self.parent.currentArea == '2':
                self.parent.currentArea = str(int(self.parent.currentArea) + 1)
                print('change area:' + self.parent.currentArea)
                self.INFO(f'change area:{self.parent.currentArea}')

                self.device.clickLocation((300, 300), AssetResponse.ASSET_SHOW, assets.in_Simulation_choice_sign)
                self.parent.initEffectInfo()
                if self.device.isVisible(assets.in_simulation_next_area):
                    self.device.click(assets.in_simulation_next_area, AssetResponse.ASSET_HIDE)
                    return

            elif self.parent.currentArea == '3':
                # 模拟结束
                self.device.clickLocation((300, 300), AssetResponse.ASSET_SHOW, assets.in_simulation_end)
                self.device.click(assets.in_simulation_end, AssetResponse.TEXT_SHOW, '模拟即将结束')
                self.device.click(assets.end_simulation_confirm, AssetResponse.TEXT_SHOW, '模拟结束')
                # 不保存
                self.parent.skipChooseEffect()
                self.device.wait(assets.in_simulation_room_sign)
                self.parent.isFinished = True
                return
