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
        if not self.checkService():
            return
        try:
            if not self.checkResolution():
                return

            if self.start():
                self.state = False
                self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
                return

            self.state = True
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
            while 1:
                for task in self.config.Task_List:
                    if Task.isActivated(self.config, task):
                        now = time.time()
                        if Task.getNextExecutionTime(self.config, task) < now:
                            self.checkService()
                            self.run(str.lower(task))

        except Exception as e:
            e = str(e)
            print(e)
            self.ui.getErrorInfo()

    def checkService(self, restart=False):
        from adbutils.errors import AdbError
        try:
            output = self.device.adb.shell("ps; ps -A")
            service = list(filter(lambda x: 'atx-agent' in x, output.split('\n')))
            if len(service) == 0:
                self.device.adb.shell('/data/local/tmp/atx-agent server -d --stop --nouia')
                self.device.stop_droidcast()

            if not self.device.u2.uiautomator.running():
                self.device.u2.uiautomator.start()
                self.device.stop_droidcast()

            if restart:
                self.socket.emit('insertLog', self.socket.getLog('INFO', 'ADB重启成功'))
                self.device.stop_droidcast()

            self.state = True
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
            return True

        except AdbError as e:
            e = str(e)
            print(e)
            if 'not found' in e:
                self.socket.emit('insertLog', self.socket.getLog('ERROR', f'{e}，当前模拟器离线，正在尝试重启ADB'))
            else:
                self.socket.emit('insertLog', self.socket.getLog('ERROR', f'{e}，正在尝试重启ADB'))

            self.state = True
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
            self.device.adb_restart()
            self.device.sleep(6)
            return self.checkService(restart=True)


        except RuntimeError as e:
            e = str(e)
            print(e)
            self.state = False
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
            if 'offline' in e:
                self.socket.emit('insertLog', self.socket.getLog('ERROR', f'{e}，当前模拟器离线'))
            else:
                self.socket.emit('insertLog', self.socket.getLog('ERROR', f'{e}'))
            self.ui.getErrorInfo()

        except ConnectionError as e:
            e = str(e)
            print(e)
            self.state = False
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
            self.socket.emit('insertLog', self.socket.getLog('ERROR', f'{e}'))
            self.ui.getErrorInfo()

        except Exception as e:
            e = str(e)
            print(e)
            self.socket.emit('insertLog', self.socket.getLog('ERROR', f'{e}，正在尝试重启ADB'))
            self.state = True
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
            self.device.adb_restart()
            self.device.sleep(6)
            return self.checkService(restart=True)

    def checkResolution(self):
        self.socket.emitSingleParameter('checkSimulator', 'info', self.device.u2.info)
        displayWidth = int(self.device.u2.info['displayWidth'])
        displayHeight = int(self.device.u2.info['displayHeight'])
        if displayWidth == 1920 and displayHeight == 1080:
            return True
        else:
            self.socket.emit('insertLog',
                             self.socket.getLog('ERROR',
                                                '模拟器分辨率错误: 必须为1920x1080，或当前模拟器非强制横屏模式'))
            self.state = False
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
        return False


if __name__ == '__main__':
    # TODO 选择服务器
    # TODO 在活动时，如果当前难度的关卡已经全部完成，但选项还开着，则关闭 待测试
    # TODO 处理弹窗礼包（在使用非加速器，升级时，或通过企业塔）待测试
    # TODO 企业塔
    # TODO 添加剩余的nikke的对话
    # TODO 咨询时没有识别到正确选项时，保存截图 待测试

    nkas = NikkeAutoScript()
    nkas.socket.run()
    # nkas.start()
