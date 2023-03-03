import cv2
from common.enum.enum import *


def matchTemplate(img=None, img_terminal=None, value=0.84, _result=None, gray=False):
    h, w, c = img_terminal.shape
    if gray:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_terminal = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(img, img_terminal, cv2.TM_CCOEFF_NORMED)
    _, sl, _, upper_left = cv2.minMaxLoc(result)
    bottom_right = (upper_left[0] + w, upper_left[1] + h)
    position = (upper_left[0], upper_left[1], bottom_right[0], bottom_right[1])
    lc = (((position[2] - position[0]) / 2 + position[0]), ((position[3] - position[1]) / 2 + position[1]))
    sl = round(sl, 2)
    res = returnResult(value, sl, lc, _result)
    if res is not None:
        return res
    else:
        return None


# @timer
def match(img=None, template=None, value=0.84, _result=None, gray=False):
    if isinstance(template, dict):
        p = template['area']
        img_terminal = cv2.imread(template['path'])[p[1]:p[3], p[0]:p[2]]
    else:
        img_terminal = template

    return matchTemplate(img, img_terminal, value, _result, gray)


def returnResult(value, sl, lc, _result):
    if sl >= value:
        if _result == ImgResult.LOCATION:
            return lc
        elif _result == ImgResult.SIMILARITY:
            return sl
        elif _result == ImgResult.LOCATION_AND_SIMILARITY:
            return lc, sl
    else:
        return None
