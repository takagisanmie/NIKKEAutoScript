import sys

from cached_property import cached_property

import assets
import glo

from module.base.task import *
from module.ui.page import *


class NikkeAutoScript:
    def __init__(self):
        glo._init()
        glo.set_value('nkas', self)
        self.state = False

    @cached_property
    def config(self):
        from module.config.config import GeneralConfig
        return GeneralConfig()

    @cached_property
    def socket(self):
        from module.socket.socket import Socket
        socket = Socket(config=self.config)
        return socket

    @cached_property
    def device(self):
        from module.device.device import Device
        device = Device(config=self.config)
        return device

    @cached_property
    def ui(self):
        from module.ui.ui import UI
        ui = UI(config=self.config, device=self.device, socket=self.socket)
        return ui

    def start(self):
        from module.handler.login import LoginHandler
        return LoginHandler(self.config, device=self.device, socket=self.socket).app_start()

    def run(self, command):
        self.device.screenshot()
        self.__getattribute__(command)()
        return True

    def reward(self):
        from module.task.reward.reward import Reward
        Reward(config=self.config, device=self.device, socket=self.socket).run()

    def destroy(self):
        from module.task.destroy.destroy import Destroy
        Destroy(config=self.config, device=self.device, socket=self.socket).run()

    def freestore(self):
        from module.task.free_store.free_store import FreeStore
        FreeStore(config=self.config, device=self.device, socket=self.socket).run()

    def conversation(self):
        from module.task.conversation.conversation import Conversation
        Conversation(config=self.config, device=self.device, socket=self.socket).run()

    def friendshippoint(self):
        from module.task.friendship_point.friendship_point import FriendshipPoint
        FriendshipPoint(config=self.config, device=self.device, socket=self.socket).run()

    def commission(self):
        from module.task.commission.commission import Commission
        Commission(config=self.config, device=self.device, socket=self.socket).run()

    def rookiearena(self):
        from module.task.rookie_arean.rookie_arena import RookieArena
        RookieArena(config=self.config, device=self.device, socket=self.socket).run()

    def simulationroom(self):
        from module.task.simulation.simulation import SimulationRoom
        SimulationRoom(config=self.config, device=self.device, socket=self.socket).run()

    def event(self):
        from module.task.event.event import Event
        Event(config=self.config, device=self.device, socket=self.socket).run()

    def loop(self):
        if self.checkResolution():
            return
        try:
            self.state = True
            if self.start():
                self.state = False
                self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
                return

            while 1:
                for task in self.config.Task_List:
                    if Task.isActivated(self.config, task):
                        now = time.time()
                        if Task.getNextExecutionTime(self.config, task) < now:
                            self.run(str.lower(task))

        except Exception as e:
            self.ui.getErrorInfo()
            del self.device.u2

    def checkResolution(self):
        if self.device.u2 is not None:
            self.socket.emitSingleParameter('checkSimulator', 'info', self.device.u2.info)
            displayWidth = int(self.device.u2.info['displayWidth'])
            displayHeight = int(self.device.u2.info['displayHeight'])
            if displayWidth == 1920 and displayHeight == 1080:
                return False

        self.socket.emit('insertLog',
                         self.socket.getLog('ERROR', '模拟器分辨率错误: 必须为1920x1080，或当前模拟器非强制横屏模式'))
        self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
        del self.device.u2
        return True


if __name__ == '__main__':

    # update
    # TODO 改进主页识别
    # TODO 咨询时跳过好感上限的nikke
    # TODO 咨询时没有识别到正确选项时，保存截图
    nkas = NikkeAutoScript()
    nkas.socket.run()
    # nkas.start()
