import assets
from common.enum.enum import *
from module.base.task import Task
from module.task.simulation.effect_control import EffectControl
from module.task.simulation.event.BattleEvent import BattleEvent
from module.task.simulation.event.BossEvent import BossEvent
from module.task.simulation.event.HealingEvent import HealingEvent
from module.task.simulation.event.ImprovementEvent import ImprovementEvent
from module.task.simulation.event.RandomEvent import RandomEvent
from module.ui.page import *
from module.ui.ui import UI

appearances = [
    assets.appearance_1,
    assets.appearance_2,
    assets.appearance_3,
]

eventType = [
    {
        'asset': assets.Battle,
        'type': EventType.BATTLE
    },
    {
        'asset': assets.Random,
        'type': EventType.RANDOM
    },
    {
        'asset': assets.Boss,
        'type': EventType.BOSS
    },
    {
        'asset': assets.Healing,
        'type': EventType.HEALING
    },
    {
        'asset': assets.Improvement,
        'type': EventType.IMPROVEMENT
    },
]

eventDifficulty = [
    {
        'asset': assets.Normal,
        'difficulty': BattleEventDifficulty.NORMAL
    },
    {
        'asset': assets.Hard,
        'difficulty': BattleEventDifficulty.HARD
    },
]


class SimulationRoom(UI, Task, EffectControl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eventList = []
        self.isFinished = False
        self.currentArea = self.config.get('Task.SimulationRoom.area', self.config.Task_Dict)

    def run(self):
        self.LINE('Simulation Room')
        if UI.current_page != page_simulation_room2:
            self.go(destination=page_simulationOption_room)
            self.chooseDifficulty()
        else:
            if lc := self.device.textStrategy('模拟结束', None, OcrResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.TEXT_SHOW, '确')

            elif lc := self.device.textStrategy('模拟结束', None, OcrResult.LOCATION, False,
                                                resized_shape=(2000, 2000)):
                self.device.clickLocation(lc, AssetResponse.TEXT_SHOW, '确')

            self.device.clickTextLocation('确', AssetResponse.ASSET_SHOW, False, assets.in_simulation_room_sign)
            UI.current_page = page_simulation_room
            self.go(destination=page_simulationOption_room)
            self.chooseDifficulty()

        while 1:
            self.initEvent()
            eventList = sorted(self.eventList, key=lambda event: event.eventType)
            print(eventList[0].eventType)
            eventList[0].run()
            if self.isFinished:
                break

        self.device.click(assets.home, AssetResponse.ASSET_HIDE)
        self.finish(self.config, 'SimulationRoom')
        self.INFO('Simulation Room is finished')

    def initEvent(self):
        self.device.wait(assets.in_Simulation_BUFF)
        self.device.wait(assets.in_Simulation_reset_time)
        self.eventList.clear()
        eventCount = len(self.device.textStrategy(None, assets.in_Simulation_effect_area, OcrResult.ALL_RESULT, True))
        position = appearances[eventCount - 1]['area']
        for i in range(eventCount):
            for event_type in eventType:
                event_position = self.device.matchRelative(position, (171 * i), (171 * i), 0, 0, event_type['asset'],
                                                           0.94, ImgResult.POSITION, i)
                if event_position:
                    if event_type['type'] == EventType.BATTLE:
                        self.eventList.append(
                            BattleEvent(event_position, self.initDifficulty(i, event_position), self, self.config,
                                        self.device, self.socket))
                        continue

                    elif event_type['type'] == EventType.HEALING:
                        self.eventList.append(
                            HealingEvent(event_position, EventType.HEALING, self, self.config, self.device,
                                         self.socket))
                        continue

                    elif event_type['type'] == EventType.IMPROVEMENT:
                        self.eventList.append(
                            ImprovementEvent(event_position, EventType.IMPROVEMENT, self, self.config, self.device,
                                             self.socket))
                        continue

                    elif event_type['type'] == EventType.RANDOM:
                        self.eventList.append(
                            RandomEvent(event_position, EventType.RANDOM, self, self.config, self.device,
                                        self.socket))
                        continue

                    elif event_type['type'] == EventType.BOSS:
                        self.eventList.append(
                            BossEvent(event_position, EventType.BOSS, self, self.config, self.device,
                                      self.socket))
                        continue

    def initDifficulty(self, id, event_position):
        for index, difficulty in enumerate(eventDifficulty):
            sl = self.device.matchRelative(event_position, 0, -110, 0, -83, difficulty['asset'], 0.45,
                                           ImgResult.SIMILARITY, id)

            if sl is not None and sl > 0.45:
                if difficulty['difficulty'] == BattleEventDifficulty.NORMAL:
                    return EventType.BATTLE
                elif difficulty['difficulty'] == BattleEventDifficulty.HARD:
                    return EventType.HARD_BATTLE

    def chooseDifficulty(self):
        from module.tools.match import match
        difficulty = self.config.get('Task.SimulationRoom.difficulty', self.config.Task_Dict)
        area = self.config.get('Task.SimulationRoom.area', self.config.Task_Dict)
        lc = None
        if difficulty == '1':
            lc = match(self.device.image, assets.Level_1, 0.84, ImgResult.LOCATION)
        elif difficulty == '2':
            lc = match(self.device.image, assets.Level_2, 0.84, ImgResult.LOCATION)
        elif difficulty == '3':
            lc = match(self.device.image, assets.Level_3, 0.84, ImgResult.LOCATION)
        elif difficulty == '4':
            lc = match(self.device.image, assets.Level_4, 0.84, ImgResult.LOCATION)
        elif difficulty == '5':
            lc = match(self.device.image, assets.Level_5, 0.84, ImgResult.LOCATION)

        self.device.multiClickLocation(lc, 2, AssetResponse.NONE)

        if area == '1':
            lc = match(self.device.image, assets.area_A, 0.84, ImgResult.LOCATION)
        elif area == '2':
            lc = match(self.device.image, assets.area_B, 0.84, ImgResult.LOCATION)
        elif area == '3':
            lc = match(self.device.image, assets.area_C, 0.84, ImgResult.LOCATION)

        self.device.multiClickLocation(lc, 2, AssetResponse.NONE)
        self.device.multiClickLocation((960, 880), 2, AssetResponse.NONE)
        for i in range(6):
            self.device.sleep(1)
            if self.device.isVisible(assets.in_Simulation_BUFF, 0.84, True):
                return
        self.chooseDifficulty()
