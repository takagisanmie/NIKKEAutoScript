import cv2
import numpy as np

from common.enum.enum import *


def matchTemplate(img=None, img_terminal=None, value=0.8, _result=None, gray=False):
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
def match(img=None, template=None, value=0.8, _result=None, gray=False):
    if isinstance(template, dict):
        p = template['area']
        img_terminal = cv2.imread(template['path'])[p[1]:p[3], p[0]:p[2]]
    else:
        img_terminal = template

    return matchTemplate(img, img_terminal, value, _result, gray)


def matchAllTemplate(img: cv2.imdecode = None, templates: list = None, img_template: dict = None, value: float = 0.8,
                     gray: bool = False, relative_locations: list = None, max_count: int = None, min_count: int = None,
                     sort_by: str = 'top', mask_id: str = None, once: bool = False):
    if mask_id:
        import glo
        mask_list = glo.get_value(mask_id)
        _img = glo.getDevice().image
        mask = np.zeros(_img.shape[:2], np.uint8)

        if mask_list:
            for mp in mask_list:
                mask[mp[0]:mp[1], mp[2]:mp[3]] = 255
                img = cv2.bitwise_and(img, img, mask=cv2.bitwise_not(mask))

    # 如果有模板，则截取为模板大小
    if img_template:
        p = img_template['area']
        img = img[p[1]:p[3], p[0]:p[2]]

    if not img.size:
        return None

    if gray:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    while 1:
        flag = False
        for index, template in enumerate(templates):
            id = template['id']
            p = template['area']
            _template = template
            template = cv2.imread(template['path'])[p[1]:p[3], p[0]:p[2]]

            if gray:
                template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            h, w = template.shape[:2]
            mask = np.zeros(img.shape[:2], np.uint8)

            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            _, sl, _, upper_left = cv2.minMaxLoc(result)
            sl = round(sl, 2)

            print(id, sl)

            if sl > value:

                bottom_right = (upper_left[0] + w, upper_left[1] + h)
                position = (upper_left[0], upper_left[1], bottom_right[0], bottom_right[1])

                left = position[0]
                right = position[2]
                top = position[1]
                bottom = position[3]

                # 去除已经匹配到的标识
                mask[top:bottom, left:right] = 255
                img = cv2.bitwise_and(img, img, mask=cv2.bitwise_not(mask))

                if img_template:
                    img_template_left = img_template['area'][0]
                    img_template_top = img_template['area'][1]

                    left += img_template_left
                    right += img_template_left
                    top += img_template_top
                    bottom += img_template_top

                if mask_id:
                    import glo
                    mask_list = glo.get_value(mask_id)
                    mask_list.append((top, bottom, left, right))
                    glo.set_value(mask_id, mask_list)
                    glo.set_value('mask_img', img)

                lc = (((right - left) / 2 + left), ((bottom - top) / 2 + top))
                x, y = int(lc[0]), int(lc[1])
                id = id.replace('_2', '')
                id = id.replace('_3', '')
                info = {
                    'id': id,
                    'location': (x, y),
                    'top': top,
                    'bottom': bottom,
                    'left': left,
                    'right': right,
                    'template': _template
                }

                relative_locations.append(info)
                flag = True
                break

        # cv2.imwrite(f'./pic/{time()}.png', img)
        if not relative_locations:
            return None

        if once:
            if sort_by:
                return relative_locations.sort(key=lambda x: x[sort_by])
            else:
                # 添加顺序
                return relative_locations

        if flag:
            continue

        if sort_by:
            return relative_locations.sort(key=lambda x: x[sort_by])
        else:
            # 添加顺序
            return relative_locations


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


def resize(img, asset=None, dst=(0, 0), fx=1, fy=1, interpolation=None):
    if asset:
        p = asset['area']
        img = img[p[1]:p[3], p[0]:p[2]]

    img = cv2.resize(img, dst, fx=fx, fy=fy, interpolation=interpolation)
    return img
