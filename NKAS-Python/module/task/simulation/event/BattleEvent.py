from common.enum.enum import *
from common.exception import Timeout

from module.task.simulation.base.event_base import BaseEvent
from module.task.simulation.simulation_assets import *
from module.tools.match import match
from module.tools.timer import Timer


class BattleEvent(BaseEvent):
    def run(self):
        print('BattleEvent')
        self.INFO('start BattleEvent')
        self.initBattle()
        self.parent.get_effect_by_battle()

    def initBattle(self):
        timeout = Timer(60).start()
        confirm_timer = Timer(1, count=2).start()
        click_timer = Timer(0.3)

        if self.eventType == EventType.BATTLE:
            button = Normal_Battle
        elif self.eventType == EventType.HARD_BATTLE:
            button = Hard_Battle
        else:
            button = Boss

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(button, 0.9, True):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                confirm_timer.wait()
                continue

            if click_timer.reached() and self.device.appear_then_click(quick_battle):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(into_battle):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                self.device.sleep(15)
                continue

            if self.device.appear(auto, gary=True):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                self.device.sleep(5)
                continue

            if self.device.appear_then_click(end_battle):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(get_effect_sign) or self.device.appear(end_simulation):
                if confirm_timer.reached():
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
