import assets
from common.enum.enum import *

from module.task.simulation.base.event_base import BaseEvent


class HealingEvent(BaseEvent):
    def run(self):
        print('HealingEvent')
        self.INFO('start HealingEvent')

        self.device.multiClickLocation(self.getLocation(), 2, AssetResponse.NONE)
        while 1:
            self.device.sleep(0.6)
            if self.device.isVisible(assets.in_Simulation_BUFF, 0.84, True):
                self.device.clickLocation(self.getLocation(), AssetResponse.NONE)
                self.device.clickLocation((970, 605), AssetResponse.NONE)
            else:
                break
        self.device.screenshot()
        if self.device.textStrategy('休憩时光', assets.in_simulation_random_card_title, OcrResult.TEXT):
            while 1:
                self.device.screenshot()
                self.device.clickTextLocation('_恢复', AssetResponse.NONE, False, resized_shape=(2000, 2000))
                self.device.clickTextLocation('确认', AssetResponse.NONE, False, resized_shape=(2000, 2000))
                if self.device.textStrategy('_恢复', None, OcrResult.TEXT, True) is None:
                    self.finish()
                    return
        else:
            self.run()
