from common.enum.enum import *
from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer, getTaskResetTime
from module.ui.page import *
from module.ui.ui import UI
from module.task.reward.reward_assets import *


class Reward(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recordTwiceTime = int(self.config.get('Task.Reward.recordTwiceTime', self.config.Task_Dict))
        self.nextExecutionTime = int(self.config.get('Task.Reward.nextExecutionTime', self.config.Task_Dict))
        self.arena = int(self.config.get('Task.Reward.arena', self.config.Task_Dict))

    def run(self):
        self.LINE('Reward')
        self.go(destination=page_reward_box)
        self.getReward(get_reward)
        self.go(destination=page_friends)
        self.send_and_receive_social_point()
        if self.arena:
            self.go(destination=page_special_arena)
            self.get_special_arena_reward()
        self._finish()
        self.INFO('Reward is finished')

    def _finish(self):
        import time
        if time.time() >= self.recordTwiceTime:
            self.when(self.config, 'Reward', 300)
        else:
            self.finish(self.config, 'Reward')

        key = 'Task.Reward.recordTwiceTime'
        self.config.update(key, getTaskResetTime(), self.config.Task_Dict, Path.TASK)

    def send_and_receive_social_point(self):
        self.device.sleep(3)
        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(send_and_receive):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                self.device.sleep(2)
                continue

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

            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(get_arean_reward):
                timeout.reset()
                click_timer.reset()
                continue

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def getReward(self, button):
        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()
            if self.device.appear(no_reward):
                return

            # 礼包
            if click_timer.reached() and self.device.appear(gift) and self.device.appear_then_click(confirm):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(gift):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(button):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

            if click_timer.reached() and self.device.hide(main_sign) and self.device.multiClickLocation((300, 300)):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()

            if self.device.appear(main_sign) and confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
