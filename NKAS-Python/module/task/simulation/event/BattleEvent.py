import glo
from assets import *
from common.enum.enum import *
from common.exception import Timeout
from module.task.simulation.base.event_base import BaseEvent
from module.task.simulation.simulation_assets import *
from module.tools.timer import Timer


class BattleEvent(BaseEvent):
    def run(self):
        print('BattleEvent')
        self.INFO('start BattleEvent')
        failed = self.initBattle()
        if failed:
            self.stop_simulation()
            return

        self.parent.get_effect_by_battle()

    def initBattle(self):
        timeout = Timer(60).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        if self.eventType == EventType.BATTLE:
            button = Normal_Battle
        elif self.eventType == EventType.HARD_BATTLE:
            button = Hard_Battle
        else:
            button = Boss

        failed = False

        while 1:
            self.device.screenshot()

            if not failed and click_timer.reached() and self.device.appear_then_click(button, gray=True):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                confirm_timer.wait()
                continue

            # 队伍没有满人
            if not failed and click_timer.reached() and self.device.appear_then_click(empty_position):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not failed and click_timer.reached() and self.device.appear(
                    empty_position_small) and self.device.appear_then_click(auto_formation):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not failed and click_timer.reached() and self.device.appear_then_click(save_formation):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not failed and click_timer.reached() and self.device.appear_then_click(quick_battle):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not failed and click_timer.reached() and self.device.appear_then_click(into_battle):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                self.device.sleep(15)
                continue

            if not failed and click_timer.reached() and self.device.appear_then_click(auto_shoot):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not failed and click_timer.reached() and self.device.appear_then_click(auto_burst):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not failed and self.device.appear(auto, gray=True):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                self.device.sleep(5)
                continue

            if not failed and self.device.appear_then_click(end_battle):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(operation_failed) and self.device.appear_then_click(end_battle_back):
                failed = True
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                self.WARNING('current battle is failed')
                self.WARNING('NKAS will go to execute the next task')
                continue

            if failed and self.device.appear(reset_time):
                return failed

            if not failed and self.device.appear(get_effect_sign) or self.device.appear(end_simulation):
                if confirm_timer.reached():
                    return False

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def stop_simulation(self):
        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear(reset_time) and self.device.hide(
                    home) and self.device.multiClickLocation((100, 200)):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(home):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.appear(main_sign) and confirm_timer.reached():
                self.parent.is_finished = True
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def end_simulation(self):

        glo.set_value('end_simulation', [])
        mask_id = 'end_simulation'

        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        reset_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(cancel, mask_id=mask_id):
                timeout.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(confirm, mask_id=mask_id):
                timeout.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(simulation_room_sign):
                if confirm_timer.reached():
                    self.parent.is_finished = True
                    return

            if reset_timer.reached():
                reset_timer.reset()
                glo.set_value(mask_id, [])

            # if click_timer.reached() \
            #         and self.device.hide(confirm) \
            #         and self.device.appear_then_click(end_simulation_button):
            #     timeout.reset()
            #     confirm_timer.reset()
            #     continue

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

            self.device.sleep(1)
