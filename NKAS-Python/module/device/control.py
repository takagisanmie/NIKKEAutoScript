import cv2

from common.enum.enum import *
from common.annotation.annotation import response
from module.device.method.droidcast import DroidCast
# from module.device.method.uiautomator_2 import Uiautomator2
from module.device.ocr import Ocr
from module.tools.utils import random_rectangle_point
from module.tools.match import match


class Control(DroidCast, Ocr):

    @response
    def click(self, button, then, *args, **kwargs):
        x, y = random_rectangle_point(button['area'])
        self.uiautomator_click(x, y)
        return [self, button, then, *args, *kwargs]

    @response
    def clickLocation(self, location, then, *args, **kwargs):
        self.uiautomator_click(location[0], location[1])
        return [self, location, then, *args, *kwargs]

    @response
    def clickTextLocation(self, text, then, screenshot=False, *args, **kwargs):
        lc = self.ocrByAsset(text, None, OcrResult.LOCATION, screenshot, *args, **kwargs)
        if lc is not None:
            self.uiautomator_click(lc[0], lc[1])
            return [self, text, then, *args, *kwargs]
        else:
            return [self, text, then, *args, *kwargs]

    def multiClickLocation(self, location, count, then, *args, **kwargs):
        for i in range(count):
            self.uiautomator_click(location[0], location[1])
            self.sleep(0.15)

        if then == AssetResponse.ASSET_SHOW:
            asset = args[0]
            self.screenshot()
            if self.isVisible(asset):
                return
            else:
                self.multiClickLocation(location, count, then, *args, **kwargs)

        if then == AssetResponse.NONE:
            return

    def textStrategy(self, text, asset, _result, screenshot=False, *args, **kwargs):
        result = self.ocrByAsset(text, asset, _result, screenshot, *args, **kwargs)
        if result is not None:
            return result
        else:
            return None

    def wait(self, template=None, value=0.84, screenshot=True, sleep=0.5):
        while 1:
            if screenshot:
                self.screenshot()
            if self.isVisible(template, value):
                return True
            self.sleep(sleep)

    def ocr(self, *args, **kwargs):
        return self._ocr(self.image, *args, **kwargs)

    def ocrByAsset(self, *args, **kwargs):
        if args[3] is True:
            self.screenshot()
        return self._ocrByAsset(self.image, *args, **kwargs)

    def isVisible(self, template=None, value=0.84, screenshot=False):
        if screenshot:
            self.screenshot()

        sl = match(img=self.image, template=template, _result=ImgResult.SIMILARITY, value=value)
        if sl is not None:
            return True
        else:
            return None

    def isHidden(self, template=None, value=0.84, screenshot=False):
        if screenshot:
            self.screenshot()

        sl = match(img=self.image, template=template, _result=ImgResult.SIMILARITY, value=value)
        if sl is None:
            return True
        else:
            return None

    def matchRelative(self, position, add_x, add_x2, add_y, add_y2, template, value=0.84, _result=None, index=None):
        x, y, x2, y2 = int(position[0]), int(position[1]), int(position[2]), int(position[3])
        # x, y, x2, y2 = position[0], position[1], position[2], position[3]

        x += add_x
        x2 += add_x2
        y += add_y
        y2 += add_y2
        img = self.image[y:y2, x:x2]
        # img = cv2.imread(Path.SCREENSHOT_PATH)[y:y2, x:x2]
        # cv2.imwrite(f'./pic/img{template["id"]}{index}.png', img)
        sl = match(img, template, value, ImgResult.SIMILARITY)
        # print(index, template['id'], sl)
        if sl and _result == ImgResult.SIMILARITY:
            return sl
        if sl and _result == ImgResult.POSITION:
            return (x, y, x2, y2)
        elif sl and _result == ImgResult.POSITION_AND_SIMILARITY:
            return (x, y, x2, y2), sl
