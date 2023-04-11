import time
from datetime import datetime, timedelta
from functools import cached_property

import inflection

import glo
from module.config.config import NikkeConfig
from module.config.utils import deep_get, deep_set
from module.exception import RequestHumanTakeover, GameNotRunningError
from module.logger import logger


class NikkeAutoScript:
    def __init__(self, config_name='nkas'):
        glo._init()
        glo.set_value('nkas', self)
        logger.hr('Start', level=0)
        self.config_name = config_name

    @cached_property
    def config(self):
        try:
            config = NikkeConfig(config_name=self.config_name)
            return config
        except RequestHumanTakeover:
            logger.critical('Request human takeover')
            exit(1)
        except Exception as e:
            logger.exception(e)
            exit(1)

    @cached_property
    def device(self):
        try:
            from module.device.device import Device
            device = Device(config=self.config)
            return device
        except RequestHumanTakeover:
            logger.critical('Request human takeover')
            exit(1)
        except Exception as e:
            logger.exception(e)
            exit(1)

    def run(self, command):
        try:
            self.device.screenshot()
            self.__getattribute__(command)()
            return True
        except GameNotRunningError as e:
            logger.warning(e)
            self.config.task_call('Restart')
            return True

    def restart(self):
        from module.handler.login import LoginHandler
        LoginHandler(self.config, device=self.device).app_restart()

    def start(self):
        from module.handler.login import LoginHandler
        LoginHandler(self.config, device=self.device).app_start()

    def reward(self):
        from module.reward.reward import Reward
        Reward(config=self.config, device=self.device).run()

    def wait_until(self, future):
        """
            Wait until a specific time.

            Args:
                future (datetime):

            Returns:
                bool: True if wait finished, False if config changed.
        """
        future = future + timedelta(seconds=1)
        # self.config.start_watching()
        while 1:
            if datetime.now() > future:
                return True
            # if self.stop_event is not None:
            #     if self.stop_event.is_set():
            #         logger.info("Update event detected")
            #         logger.info(f"[{self.config_name}] exited. Reason: Update")
            #         exit(0)

            time.sleep(5)
            # if self.config.should_reload():
            #     return False

    def get_next_task(self):
        """
            Returns:
                str: Name of the next task.
        """
        while 1:
            task = self.config.get_next()
            self.config.task = task
            '''
                在 Alas 中每个任务都有共有属性 Scheduler
                调度器在运行任务时，是根据任务的 Scheduler.Command 调用对应方法
                在那之前，Alas 会调用 config.bind(task)
                将该任务的 Scheduler 属性覆盖到类变量
                在使用到共有属性时，只会使用该任务的设置
                例如在设置任务的下次运行时间时，会使用到 Scheduler.SuccessInterval
                interval = (self.Scheduler_SuccessInterval if success else self.Scheduler_FailureInterval)
                run.append(datetime.now() + ensure_delta(interval))
            '''
            self.config.bind(task)
            from module.base.resource import release_resources

            if task.next_run > datetime.now():
                logger.info(f'Wait until {task.next_run} for task `{task.command}`')
                release_resources()
                if not self.wait_until(task.next_run):
                    '''
                        在等待任务的过程中可能会被人为修改运行时间
                    '''
                    # 当 self.config.should_reload() 为 True 时 wait_until 会返回 False
                    del self.__dict__['config']
                    continue

            if self.config.task.command != 'NKAS':
                release_resources(next_task=task.command)
            break

        return task.command

    def loop(self):
        logger.set_file_logger(self.config_name)
        logger.info(f'Start scheduler loop: {self.config_name}')
        is_first = True
        failure_record = {}

        while 1:
            task = self.get_next_task()
            _ = self.device

            if is_first and task == 'Restart':
                logger.info('Skip task `Restart` at scheduler start')
                self.config.task_delay(server_update=True)
                del self.__dict__['config']
                continue

            # Run
            logger.info(f'Scheduler: Start task `{task}`')
            self.device.stuck_record_clear()
            self.device.click_record_clear()
            logger.hr(task, level=0)
            '''
            
                https://inflection.readthedocs.io/en/latest/
                
                inflection.underscore('Restart') => 'restart'
                inflection.underscore('DeviceType') => 'device_type'
                
            '''
            success = self.run(inflection.underscore(task))
            logger.info(f'Scheduler: End task `{task}`')
            is_first = False

            # Check failures
            failed = deep_get(failure_record, keys=task, default=0)
            failed = 0 if success else failed + 1
            deep_set(failure_record, keys=task, value=failed)
            if failed >= 3:
                logger.critical(f"Task `{task}` failed 3 or more times.")
                logger.critical("Possible reason #1: You haven't used it correctly. "
                                "Please read the help text of the options.")
                logger.critical("Possible reason #2: There is a problem with this task. "
                                "Please contact developers or try to fix it yourself.")
                logger.critical('Request human takeover')
                exit(1)

            if success:
                del self.__dict__['config']
                continue
            else:
                break


if __name__ == '__main__':
    nkas = NikkeAutoScript()
    self = nkas
    # from module.handler.login import LoginHandler

    # e = LoginHandler(self.config, device=self.device)
    # self.device.screenshot()
    # self.start()

    # from module.task.reward.reward import Reward
    #
    # Reward(config=self.config, device=self.device).run()
    # e.ui_goto(destination=page_reward)

    # self
