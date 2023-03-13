from common.enum.enum import *
from module.device.method.droidcast import DroidCast
from module.device.ocr import Ocr
from module.tools.utils import random_rectangle_point
from module.tools.match import match, matchAllTemplate
from module.ui.page import Button


class Control(DroidCast, Ocr):

    def click(self, button):
        x, y = random_rectangle_point(button['area'])
        self.uiautomator_click(x, y)
        return True

    def appear_then_click(self, button, value=0.8, screenshot=False, gray=False, img=None, img_template=None,
                          mask_id=None, index=0):

        # if 'button' in button.keys():
        #     _button: Button = button['button']
        #     template = _button.template
        #     lc = _button.location
        #
        #     if self.appear(template, value, screenshot=screenshot, _result=ImgResult.LOCATION, gray=gray, img=img,
        #                    img_template=img_template, mask_id=mask_id, index=index):
        #         self.uiautomator_click(lc[0], lc[1])
        #         return True
        #     else:
        #         return False

        if lc := self.appear(button, value, screenshot=screenshot, _result=ImgResult.LOCATION, gray=gray, img=img,

                             img_template=img_template, mask_id=mask_id, index=index):

            # x, y = random_rectangle_point(button['area'])

            # print(button['id'], lc)

            self.uiautomator_click(lc[0], lc[1])

            return True

        else:

            return False

    def clickTextLocation(self, text, screenshot=False, *args, **kwargs):
        lc = self.ocrByAsset(text, None, OcrResult.LOCATION, screenshot, *args, **kwargs)
        if lc is not None:
            self.uiautomator_click(lc[0], lc[1])
            return True
        else:
            return False

    def multiClickLocation(self, location, count=2, delay=0.15):
        for i in range(count):
            self.uiautomator_click(location[0], location[1])
            self.sleep(delay)

        return True

    def multiClick(self, button, count, delay=0.15):
        for i in range(count):
            x, y = random_rectangle_point(button['area'])
            self.uiautomator_click(x, y)
            self.sleep(delay)

        return True

    def textStrategy(self, text, asset, _result, line=False, screenshot=False, *args, **kwargs):
        result = self.ocrByAsset(text, asset, _result, line, screenshot, *args, **kwargs)
        if result is not None:
            return result
        else:
            return None

    def ocrByAsset(self, *args, **kwargs):
        if kwargs.get('screenshot'):
            self.screenshot()
        return self._ocrByAsset(self.image, *args, **kwargs)

    def appear(self, template=None, value=0.8, _result=ImgResult.SIMILARITY, screenshot=False, gray=False,
               img=None, img_template=None, sort_by='top', mask_id=None, index=0):

        if screenshot or not hasattr(self, "image"):
            self.screenshot()

        img = self.image if screenshot or img is None else img

        # res = match(img=self.image, template=template, _result=_result, value=value, gray=gray)

        locations = []
        matchAllTemplate(img, [*template] if isinstance(template, list) else [template], img_template=img_template,
                         value=value,
                         gray=gray,
                         relative_locations=locations, sort_by=sort_by, mask_id=mask_id)

        if _result == ImgResult.ALL_RESULT:
            return locations

        elif locations:
            return locations[index]['location']
        else:
            return None

    def hide(self, template=None, value=0.8, _result=ImgResult.SIMILARITY, screenshot=False, gray=False,
             img=None, img_template=None, sort_by='top', mask_id=None):

        if screenshot or not hasattr(self, "image"):
            self.screenshot()

        img = self.image if screenshot or img is None else img

        # res = match(img=self.image, template=template, _result=_result, value=value, gray=gray)

        locations = []
        matchAllTemplate(img, [*template] if isinstance(template, list) else [template], img_template=img_template,
                         value=value,
                         gray=gray,
                         relative_locations=locations, sort_by=sort_by, mask_id=mask_id)

        if not locations:
            return True
        else:
            return None

    def _hide(self, template=None, value=0.8, screenshot=False):
        if screenshot:
            self.screenshot()

        sl = match(img=self.image, template=template, _result=ImgResult.SIMILARITY, value=value)
        if sl is None:
            return True
        else:
            return None

    def matchRelative(self, position, add_x, add_x2, add_y, add_y2, template, value=0.8, _result=None, index=None):
        x, y, x2, y2 = int(position[0]), int(position[1]), int(position[2]), int(position[3])
        # left,top,right,bottom
        # x, y, x2, y2 = position[0], position[1], position[2], position[3]

        x += add_x
        x2 += add_x2
        y += add_y
        y2 += add_y2
        img = self.image[y:y2, x:x2]
        # img = cv2.imread(Path.SCREENSHOT_PATH)[y:y2, x:x2]
        # cv2.imwrite(f'./pic/img-{template["id"]}{time.time()}.png', img)

        sl = match(img, template, value, ImgResult.SIMILARITY)

        # print(index, templates['id'], sl)
        if sl and _result == ImgResult.SIMILARITY:
            return sl
        if sl and _result == ImgResult.POSITION:
            return (x, y, x2, y2)
        elif sl and _result == ImgResult.POSITION_AND_SIMILARITY:
            return (x, y, x2, y2), sl
