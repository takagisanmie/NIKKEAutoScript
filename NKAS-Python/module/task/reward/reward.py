from common.enum.enum import *
from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from module.task.reward.reward_assets import *


class Reward(UI, Task):
    def run(self):
        self.LINE('Reward')
        self.go(destination=page_reward_box)
        self.getReward(get_reward)
        self.go(destination=page_friends)
        self.send_and_receive_social_point()
        # TODO 可能没有解锁
        self.go(destination=page_special_arena)
        self.get_special_arena_reward()

        self.finish(self.config, 'Reward')
        self.INFO('Reward is finished')

    def send_and_receive_social_point(self):
        self.device.sleep(3)
        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(0.8)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(send_and_receive):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

            if click_timer.reached() and self.device.appear_then_click(confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def get_special_arena_reward(self):
        timeout = Timer(20).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()
            if self.device.appear(no_special_arena_point) or self.device.appear(no_special_arena_point_2):
                return

            if click_timer.reached() and self.device.appear_then_click(get_arean_reward):
                timeout.reset()
                click_timer.reset()

            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                click_timer.reset()

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def getReward(self, button):
        timeout = Timer(10).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(0.5)

        while 1:
            self.device.screenshot()
            if self.device.appear(no_reward):
                return

            if click_timer.reached() and self.device.appear_then_click(button):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
