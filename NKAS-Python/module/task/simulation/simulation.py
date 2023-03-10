import time
from common.exception import Timeout
from module.base.task import Task
from module.task.simulation.simulation_assets import *
from module.task.simulation.effect_control import EffectControl
from module.task.simulation.event.BattleEvent import BattleEvent
from module.task.simulation.event.BossEvent import BossEvent
from module.task.simulation.event.HealingEvent import HealingEvent
from module.task.simulation.event.ImprovementEvent import ImprovementEvent
from module.task.simulation.event.RandomEvent import RandomEvent
from module.tools.match import *
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI


class SimulationRoom(UI, Task, EffectControl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.end_area = int(self.config.get('Task.SimulationRoom.end_area', self.config.Task_Dict))
        self.is_finished = False

    def run(self):
        self.LINE('Simulation Room')
        self.go_to_simulation()
        self.check_level_and_area()
        # self.check_own_effects()
        # 处于事件选择
        while 1:
            self.matchEvents()
            if self.is_finished:
                break

        self.device.appear_then_click(home)
        self.finish(self.config, 'SimulationRoom')
        self.INFO('Simulation Room is finished')

    def check_level_and_area(self):
        self.device.screenshot()
        if self.device.appear(area_a, gary=True):
            self.current_area = 1
        elif self.device.appear(area_b, gary=True):
            self.current_area = 2
        elif self.device.appear(area_c, gary=True):
            self.current_area = 3

    def matchEvents(self):
        event_list = []
        self.device.screenshot()
        matchAllTemplate(img=self.device.image,
                         templates=[Normal_Battle, Hard_Battle, Random, Improvement, Healing, Boss],
                         img_template=event_list_area, value=0.84, gray=True, relative_locations=event_list,
                         max_count=3,
                         min_count=1, sort_by='left')

        # if e := list(filter(lambda x: x['id'] == 'Normal_Battle', event_list)):
        #     BattleEvent(EventType.BATTLE, self, self.config, self.device, self.socket).run()
        #
        # elif e := list(filter(lambda x: x['id'] == 'Random', event_list)):
        #     RandomEvent(EventType.RANDOM, self, self.config, self.device, self.socket).run()

        if e := list(filter(lambda x: x['id'] == 'Random', event_list)):
            RandomEvent(EventType.RANDOM, self, self.config, self.device, self.socket).run()

        elif e := list(filter(lambda x: x['id'] == 'Normal_Battle', event_list)):
            BattleEvent(EventType.BATTLE, self, self.config, self.device, self.socket).run()

        elif e := list(filter(lambda x: x['id'] == 'Improvement', event_list)):
            ImprovementEvent(EventType.IMPROVEMENT, self, self.config, self.device, self.socket).run()

        elif e := list(filter(lambda x: x['id'] == 'Healing', event_list)):
            HealingEvent(EventType.HEALING, self, self.config, self.device, self.socket).run()

        elif e := list(filter(lambda x: x['id'] == 'Boss', event_list)):
            BossEvent(EventType.BOSS, self, self.config, self.device, self.socket).run()

        elif e := list(filter(lambda x: x['id'] == 'Hard_Battle', event_list)):
            BattleEvent(EventType.HARD_BATTLE, self, self.config, self.device, self.socket).run()

    def choose_difficulty(self):
        difficulty = int(self.config.get('Task.SimulationRoom.difficulty', self.config.Task_Dict))
        area = int(self.config.get('Task.SimulationRoom.area', self.config.Task_Dict))

        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=2).start()

        difficulties = [Level_1, Level_2, Level_3, Level_4, Level_5]
        areas = [Area_A, Area_B, Area_C]

        while 1:
            self.device.screenshot()
            if self.device.appear_then_click(difficulties[difficulty - 1]):
                timeout.reset()

            if self.device.appear_then_click(areas[area - 1]):
                timeout.reset()

            if self.device.appear_then_click(to_simulation):
                timeout.reset()

            if self.device.appear(reset_time):
                if confirm_timer.reached():
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def check_own_effects(self):

        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=2).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()
            if click_timer.reached() and self.device.appear_then_click(own_effect_list):
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(own_effect_list_sign):
                if confirm_timer.reached():
                    break

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

        for i in range(2):
            self.device.swipe(360, 570, 360, 930, 0.1)
            self.device.sleep(1)

        self.getCurrentEffects(area=own_effect_list_area)

        timeout.reset()
        click_timer.reset()
        confirm_timer.reset()

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(confirm):
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.device.hide(own_effect_list_sign):
                if confirm_timer.reached():
                    break

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def go_to_simulation(self):
        self.where()
        if UI.current_page is page_simulation_room:
            self.go(destination=page_simulation_option)
            self.choose_difficulty()
            return

        elif UI.current_page is page_simulation_option:
            self.choose_difficulty()
            return

        elif UI.current_page is page_simulation:
            return

        self.go(destination=page_ark)

        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(0.3)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(to_simulation_room):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(simulation_room_sign):
                UI.current_page = page_simulation_room
                self.go_to_simulation()
                return

            # 已经开始过
            if self.device.appear(reset_time):
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
