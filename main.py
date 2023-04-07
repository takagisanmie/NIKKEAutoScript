from functools import cached_property

import glo
from module.config.config import NikkeConfig
from module.exception import RequestHumanTakeover
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

    def start(self):
        from module.handler.login import LoginHandler
        LoginHandler(self.config, device=self.device).app_start()

    # def reward(self):
    #     from module.task.reward.reward import Reward
    #     Reward(config=self.config, device=self.device).run()

    def loop(self):
        self.start()


if __name__ == '__main__':
#    test
    nkas = NikkeAutoScript()
    self = nkas
    from module.handler.login import LoginHandler

    e = LoginHandler(self.config, device=self.device)
    # self.device.screenshot()
    self.start()
    # e.device.screenshot()
    # print(e.appear(CONFRIM_A, offset=(30, 30), interval=5, static=False))
    # e.appear_then_click(CONFRIM_A, offset=(30, 30), interval=5, static=False)
    # x, y = rectangle_point(CONFRIM_A.button)
    # e.device.click_minitouch(100, 930.5)
    # print(x, y)
