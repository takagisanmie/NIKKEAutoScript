import assets
from common.enum.enum import *

from module.base.base import BaseModule
from module.task.simulation.base.effect import Effect

effects = [
    assets.effect_A,
    assets.effect_B,
    assets.effect_C,
]


class EffectControl(BaseModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.effectList = []
        self.availableEffectList = []

    def getEffectByBattle(self):
        from module.tools.match import match
        if len(self.effectList) < 8 and len(self.availableEffectList) > 0:
            availableEffectList = sorted(self.availableEffectList, key=lambda dict_: dict_["priority"])
            self.device.multiClickLocation(self.getLocation(availableEffectList[0]['position']), 2, AssetResponse.NONE)
            name = availableEffectList[0]['name']
            displayName = availableEffectList[0]['displayName']
            priority = availableEffectList[0]['priority']
            # type =availableEffectList[0]['type']
            # TODO 识别品质和形状
            # quality =
            # shape =
            self.effectList.append(Effect(name, displayName, priority, None, None, None))
            if lc := match(self.device.image, assets.choose_new_effect_confirm, 0.84, ImgResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.NONE)
        else:
            self.notChooseEffectByBattle()

        self.device.sleep(1.2)
        # 选择完成
        if self.device.isVisible(assets.in_Simulation_BUFF, 0.84, True):
            return
        # 选择到了效果一样，适用对象一样，品质和形状可能不一样的增益
        elif self.device.textStrategy('已持有相同效果的增益效果', None, OcrResult.TEXT):
            # TODO 在拥有列表中通过对比已有增益，找到位置
            # TODO 进行形状对比，品质对比，再做出选择
            # 暂时先不替换
            self.device.clickTextLocation('取消', AssetResponse.ASSET_SHOW, False, assets.in_Simulation_choice_sign)
            self.notChooseEffectByBattle()

        # 增益到达上限
        elif self.device.textStrategy('已达上限', None, OcrResult.TEXT):
            self.device.clickTextLocation('取消', AssetResponse.ASSET_SHOW, False, assets.in_Simulation_choice_sign)
            self.notChooseEffectByBattle()

        else:
            self.getEffectByBattle()

    def notChooseEffectByBattle(self):
        self.device.clickTextLocation('不选择', AssetResponse.TEXT_SHOW, False, '不选择增益效果')
        self.device.click(assets.confirm, AssetResponse.TEXT_HIDE, '不选择增益效果')
        pass

    def skipChooseEffect(self):
        while 1:
            if lc := self.device.textStrategy('不选择', None, OcrResult.LOCATION, True, resized_shape=(2000, 2000)):
                self.device.multiClickLocation(lc, 1, AssetResponse.NONE)

            if lc := self.device.textStrategy('确认', None, OcrResult.LOCATION, True, resized_shape=(2000, 2000)):
                self.device.multiClickLocation(lc, 1, AssetResponse.NONE)

            else:
                return

    def initEffectInfo(self):
        self.availableEffectList.clear()
        self.device.wait(assets.in_Simulation_choice_sign)
        for effect_title in effects:
            et = self.device.textStrategy(None, effect_title, OcrResult.TEXT, False, resized_shape=(2000, 2000))
            if et is not None:
                for pe in preferential_effect:
                    if pe['name'] in et:
                        pe['position'] = effect_title['area']
                        self.availableEffectList.append(pe)
                        break

        self.getEffectByBattle()

    def getCurrentEffectCount(self):
        self.device.click(assets.in_Simulation_effect_list, AssetResponse.TEXT_SHOW, '拥有的增益效果')

        pass

    def getLocation(self, position):
        lc = (((position[2] - position[0]) / 2 + position[0]), ((position[3] - position[1]) / 2 + position[1]))
        return lc


preferential_effect = [
    {
        'displayName': '高品质粉末',
        'name': '高品质粉末',
        'priority': 1

    },
    {
        'displayName': '反射弹头',
        'name': '反射',
        'priority': 2

    },
    {
        'displayName': '超越弹匣',
        'name': '超越',
        'priority': 1

    },
    {
        'displayName': '控制引导器',
        'name': '控制引导器',
        'priority': 2

    },
    {
        'displayName': '快速弹匣',
        'name': '快速弹匣',
        'priority': 1

    },
    {
        'displayName': '引流转换器',
        'name': '引流转换器',
        'priority': 5

    },
    {
        'displayName': '连结AMO',
        'name': '连结AMO',
        'priority': 4

    },
    {
        'displayName': '艾薇拉粒子干扰丝',
        'name': '干扰丝',
        'priority': 2

    },
    {
        'displayName': '快速充电器',
        'name': '快速充电器',
        'priority': 3

    },
    {
        'displayName': '冲击引流器',
        'name': '冲击引流器',
        'priority': 3

    },
    {
        'displayName': '隐身粉',
        'name': '隐身粉',
        'priority': 3

    },
]
