from functools import cached_property

import numpy as np
from cnocr import CnOcr


class Ocr:
    @cached_property
    def cnocr(self):
        return CnOcr(rec_model_name='densenet_lite_136-fc',
                     rec_model_fp='./bin/cnocr_model/cnocr-v2.2-densenet_lite_136-fc.onnx')

    def ocr(self, img_fp):
        return self.cnocr.ocr(img_fp)

    def filter(self, result):
        if result:
            return list(filter(lambda x: x['score'] >= 0.3, result))

    def get_location(self, text, result):

        if result:
            if '_' in text:
                r = [i['position'] for i in result if text == i['text']]
            else:
                r = [i['position'] for i in result if text in i['text']]

            if r:
                upper_left, bottom_right = r[0][0], r[0][2]
                x, y = (np.array(upper_left) + np.array(bottom_right)) / 2
                return x, y


import os
import cv2

if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(__file__), '../../'))
    img = cv2.imread('./pic/t1.png')
    ocr = Ocr()
    text = '领取奖励'
    res = ocr.ocr(img)
    print(res)
    # res = ocr.filter(res)
    # location = ocr.get_location(text, res)
    # print(location)
