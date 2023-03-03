import assets
from common.enum.enum import *

from module.task.simulation.base.event_base import BaseEvent
from module.tools.match import match


class RandomEvent(BaseEvent):
    def run(self):
        print('RandomEvent')
        self.INFO('start RandomEvent')
        self.device.multiClickLocation(self.getLocation(), 2, AssetResponse.NONE)
        while 1:
            if self.device.isVisible(assets.in_Simulation_BUFF, 0.84, True):
                self.device.clickLocation(self.getLocation(), AssetResponse.NONE)
                self.device.clickLocation((970, 605), AssetResponse.NONE)
            else:
                self.device.sleep(1)
                break

        while 1:
            self.device.screenshot()
            # 取消按钮
            if lc := match(self.device.image, assets.in_Simulation_cancel, 0.84, ImgResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.TEXT_SHOW, '什么都没有发生')
                self.finish()
                return
            else:
                # 取消选项
                if lc := self.device.textStrategy('不选择', None, OcrResult.LOCATION):
                    self.device.multiClickLocation(lc, 2, AssetResponse.NONE)

                elif lc := self.device.textStrategy('第一个选项', None, OcrResult.LOCATION, False):
                    self.device.multiClickLocation(lc, 2, AssetResponse.NONE)

                elif lc := self.device.textStrategy('第二个选项', None, OcrResult.LOCATION, False):
                    self.device.multiClickLocation(lc, 2, AssetResponse.NONE)

                # TODO 下滑，选泽第三个
                self.device.clickTextLocation('确认', AssetResponse.NONE, False, resized_shape=(2000, 2000))

                # if self.device.textStrategy('个选项', None, OcrResult.LOCATION, True) is None:
                #     break

                if self.device.textStrategy('结果', None, OcrResult.TEXT, False, resized_shape=(2000, 2000)):
                    self.finish()
                    return
                elif self.device.textStrategy('请选择', None, OcrResult.TEXT):
                    self.finish()
                    return
