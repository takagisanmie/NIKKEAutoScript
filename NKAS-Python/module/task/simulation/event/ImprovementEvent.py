import assets
from common.enum.enum import *

from module.task.simulation.base.event_base import BaseEvent


class ImprovementEvent(BaseEvent):
    def run(self):
        print('ImprovementEvent')
        self.INFO('start ImprovementEvent')
        self.device.multiClickLocation(self.getLocation(), 2, AssetResponse.NONE)
        while 1:
            self.device.sleep(0.6)
            if self.device.isVisible(assets.in_Simulation_BUFF, 0.84, True):
                self.device.clickLocation(self.getLocation(), AssetResponse.NONE)
                self.device.clickLocation((970, 605), AssetResponse.NONE)
            else:
                break
        self.device.screenshot()
        if self.device.textStrategy('条件不符', None, OcrResult.TEXT):
            self.device.clickTextLocation('不选择', AssetResponse.TEXT_SHOW, False, '什么都没有发生')
            self.finish()
        else:
            while 1:

                self.device.screenshot()

                if lc := self.device.textStrategy('第一个选项', None, OcrResult.LOCATION, False,
                                                  resized_shape=(2000, 2000)):
                    self.device.multiClickLocation(lc, 2, AssetResponse.NONE)
                elif lc := self.device.textStrategy('第二个选项', None, OcrResult.LOCATION, False,
                                                    resized_shape=(2000, 2000)):
                    self.device.multiClickLocation(lc, 2, AssetResponse.NONE)

                if self.device.textStrategy('结果', None, OcrResult.TEXT, False, resized_shape=(2000, 2000)):
                    self.finish()
                    return
                elif self.device.textStrategy('请选择', None, OcrResult.TEXT, False, resized_shape=(2000, 2000)):
                    self.finish()
                    return
                else:
                    self.device.clickTextLocation('确认', AssetResponse.NONE)

                self.device.sleep(0.5)

                if self.device.isVisible(assets.in_Simulation_reset_time, 0.84, True):
                    if self.device.isVisible(assets.in_Simulation_BUFF, 0.84, True):
                        print('finished')
                        return
