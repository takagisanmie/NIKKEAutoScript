from cached_property import cached_property

from module.base.task import *


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

    def commission(self):
        from module.task.commission.commission import Commission
        Commission(config=self.config, device=self.device, socket=self.socket).run()

    def rookiearena(self):
        from module.task.rookie_arena.rookie_arena import RookieArena
        RookieArena(config=self.config, device=self.device, socket=self.socket).run()

    def tribetower(self):
        from module.task.tribe_tower.tribe_tower import TribeTower
        TribeTower(config=self.config, device=self.device, socket=self.socket).run()

    def simulationroom(self):
        from module.task.simulation.simulation import SimulationRoom
        SimulationRoom(config=self.config, device=self.device, socket=self.socket).run()

    def event(self):
        from module.task.event.event import Event
        Event(config=self.config, device=self.device, socket=self.socket).run()

    def daily(self):
        from module.task.daily.daily import Daily
        Daily(config=self.config, device=self.device, socket=self.socket).run()

    def loop(self):
        if not self.checkService():
            return
        try:
            if not self.checkResolution():
                return

            self.state = True
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)

            while 1:
                self.ui.stop_until_reset_time()
                all_task = self.config.get('Task')
                task_list = [self.config.get('Task.' + x) for x in all_task if self.config.get('Task.' + x)['activate']]
                task_list.sort(key=lambda x: x['nextExecutionTime'])
                task = task_list[0]['name']
                now = time.time()
                if Task.getNextExecutionTime(self.config, task) < now:

                    if not self.start():
                        self.state = False
                        self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
                        return

                    self.socket.getAllTaskStates()
                    self.run(str.lower(task))

                _task_list = list(filter(lambda x: x['nextExecutionTime'] <= time.time(), task_list))
                if not _task_list:
                    idle = self.config.get('Idle', self.config.config_dict)
                    if idle:
                        self.device.app_stop()

        except Exception as e:
            e = str(e)
            print(e)
            self.state = False
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
            self.socket.emit('insertLog', self.socket.getLog('ERROR', f'{e}'))
            self.ui.getErrorInfo()

    def checkService(self, restart=False):
        from adbutils.errors import AdbError
        try:
            if self.config.Simulator_Serial.startswith('127.0.0.1'):
                self.device.adb_client.connect(self.config.Simulator_Serial, timeout=5)
                self.device.sleep(5)

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
                self.socket.emit('insertLog', self.socket.getLog('ERROR', f'{e}，没有找到模拟器，正在尝试重启ADB'))
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
            self.state = False
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
            self.socket.emit('insertLog', self.socket.getLog('ERROR', f'{e}'))
            self.ui.getErrorInfo()

    def checkResolution(self):
        self.socket.emitSingleParameter('checkSimulator', 'info', self.device.u2.info)
        displayWidth = int(self.device.u2.info['displayWidth'])
        displayHeight = int(self.device.u2.info['displayHeight'])
        if displayWidth == 720 and displayHeight == 1280:
            return True
        else:
            self.socket.emit('insertLog',
                             self.socket.getLog('ERROR',
                                                '模拟器分辨率错误: 必须为720x1280'))
            self.state = False
            self.socket.emitSingleParameter('checkSchedulerState', 'state', self.state)
        return False

if __name__ == '__main__':
    # TODO 升级NIKKE

    # TODO 废铁商店效率过慢
    # TODO 计算活动的困难模式开启时间，在前一天或执行前跳过活动任务

    nkas = NikkeAutoScript()
    nkas.socket.run()