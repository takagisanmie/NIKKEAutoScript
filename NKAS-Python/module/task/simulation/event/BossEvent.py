
from common.enum.enum import *
from common.exception import Timeout
from module.task.simulation.event.BattleEvent import BattleEvent
from module.tools.timer import Timer
from module.task.simulation.simulation_assets import *
from assets import *


class BossEvent(BattleEvent):
    def run(self):
        print('BossEvent')
        self.INFO('start BossEvent')
        self.initBattle()

        if self.parent.current_area == 1 or self.parent.current_area == 2:
            self.parent.get_effect_by_battle()

        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(0.8)

        while 1:
            self.device.screenshot()
            if self.device.appear(end_simulation_sign):
                self.end_simulation()
                return

            if click_timer.reached() \
                    and self.parent.end_area != self.parent.current_area \
                    and self.device.appear_then_click(next_area, img_template=next_and_end_area):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(end_simulation, img_template=next_and_end_area):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.hide(end_simulation) and self.device.appear(simulation_sign):
                if confirm_timer.reached():
                    self.parent.current_area += 1
                    return

            if timeout.reached():
                raise Timeout

    def end_simulation(self):

        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(0.6)
        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(confirm):
                timeout.reset()
                confirm_timer.reset()

            if click_timer.reached() and self.device.appear_then_click(cancel):
                timeout.reset()
                confirm_timer.reset()

            if self.device.appear(simulation_room_sign):
                if confirm_timer.reached():
                    self.parent.is_finished = True
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
