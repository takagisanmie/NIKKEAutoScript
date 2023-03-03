import assets
from common.enum.enum import AssetResponse, OcrResult, ImgResult
from module.base.base import BaseModule


class BaseEvent(BaseModule):
    def __init__(self, position, eventType, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = position
        self.eventType = eventType
        self.parent = parent

    def getLocation(self, position=None):
        if position is None:
            position = self.position
        lc = (((position[2] - position[0]) / 2 + position[0]), ((position[3] - position[1]) / 2 + position[1]))
        x, y = lc[0], lc[1]
        y -= 51
        return [x, y]

    def finish(self):
        from module.tools.match import match
        while 1:
            print('finish')
            self.device.screenshot()
            if self.device.textStrategy('请选择', None, OcrResult.TEXT):
                if lc := match(self.device.image, assets.effect_sign, 0.84, ImgResult.LOCATION):
                    x, y = lc[0] - 50, lc[1] + 50
                    self.device.multiClickLocation((x, y), 2, AssetResponse.NONE)
            elif lc := self.device.textStrategy('不选择', None, OcrResult.LOCATION):
                print('不选择')
                self.device.multiClickLocation(lc, 2, AssetResponse.NONE)

            # self.device.clickTextLocation('确认', AssetResponse.TEXT_HIDE, True, '确认')
            # self.device.clickTextLocation('碓', AssetResponse.TEXT_HIDE, True, '碓', resized_shape=(2000, 2000))
            self.device.clickTextLocation('确认', AssetResponse.NONE, False, resized_shape=(2000, 2000))
            self.device.clickTextLocation('碓', AssetResponse.NONE, False, resized_shape=(2000, 2000))
            self.device.sleep(0.5)
            if self.device.isVisible(assets.in_Simulation_reset_time, 0.84, True):
                if self.device.isVisible(assets.in_Simulation_BUFF, 0.84, True):
                    print('finished')
                    return
