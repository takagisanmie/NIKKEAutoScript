import os
import cv2
import numpy as np
from cnocr import CnOcr

from main import NikkeAutoScript
from module.base.utils import area_offset, crop, _area_offset, extract_letters, show_image, find_letter_area
from module.ocr.models import OCR_MODEL
from module.rookie_arena.assets import POWER_CHECK

if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(__file__), '../../'))
    # img = cv2.imread('text079.png')
    # img = cv2.imread('text080.png')
    # img = cv2.imread('text081.png')
    # img = cv2.imread('text082.png')

    # img = cv2.imread('./pic/Screenshot_20230422-064324.png')

    nkas = NikkeAutoScript()
    self = nkas
    img = self.device.screenshot()

    # area = (82, 817, 640, 900)
    # area_2 = (82, 920, 640, 1000)
    #
    # _img = crop(img, area)
    # _img = extract_letters(_img, letter=(247, 243, 247))
    # text_rect = find_letter_area(_img < 128)
    # text_rect = _area_offset(text_rect, (-2, -2, 3, 2))
    # show_image(crop(crop(img, area), text_rect))

    ocr = OCR_MODEL.nikke.ocr
    # ocr = CnOcr()
    # print(ocr.ocr(img))

    r = [i.get('area') for i in POWER_CHECK.match_several(img, threshold=0.66, static=False)]
    r = [_area_offset(i, (22, -10, 65, 8)) for i in r]
    for index, i in enumerate(r):
        _img = crop(img, i)
        _img = extract_letters(_img, letter=(90, 93, 99))
        text_rect = find_letter_area(_img < 128)
        text_rect = _area_offset(text_rect, (-2, -2, 3, 2))
        print(ocr(crop(crop(img, i), text_rect)))
        # cv2.imwrite(f'./train/{index}.png', crop(crop(img, i), text_rect))
