import assets
from common.enum.enum import *

from module.task.simulation.base.event_base import BaseEvent


class BattleEvent(BaseEvent):
    def run(self):
        print('BattleEvent')
        self.INFO('start BattleEvent')
        self.initBattle()
        self.parent.initEffectInfo()

    def initBattle(self):
        # 点击出HP指示
        self.device.clickLocation(self.getLocation(), AssetResponse.ASSET_HIDE, assets.in_Simulation_BUFF)
        # 如果没有出现准备界面的关闭键，则点击中间
        if self.device.isHidden(assets.in_Simulation_battle_event, True):
            self.device.clickLocation((970, 605), AssetResponse.ASSET_SHOW, assets.in_Simulation_battle_event)
        # 如果当前是普通战斗，则跳过
        if self.eventType == EventType.BATTLE:
            # 进入增益选择
            self.device.click(assets.quick_battle, AssetResponse.ASSET_HIDE)
        # 如果当前是困难战斗，则进入，并等待结束
        elif self.eventType == EventType.HARD_BATTLE:
            self.device.click(assets.into_battle2, AssetResponse.ASSET_HIDE)
            self.device.wait(assets.end_battle2)
            # 进入增益选择
            self.device.clickLocation((300, 300), AssetResponse.ASSET_SHOW, assets.in_Simulation_choice_sign)
        # 如果当前是Boss战，则进入，并等待结束
        elif self.eventType == EventType.BOSS:
            self.device.click(assets.into_battle2, AssetResponse.ASSET_HIDE)
            self.device.wait(assets.end_battle2)

    pass
