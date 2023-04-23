from functools import cached_property

import numpy as np

from module.ocr.nikke_ocr import NikkeOcr


class OcrModel:
    @cached_property
    def nikke(self):
        """
            t18
            base: cnocr-v2.2-densenet_lite_136-gru.ckpt
            training data: 2156
            epochs: 15
            mainly used for the rookie arena

            t20
            base: cnocr-v2.2-densenet_lite_136-gru.ckpt
            training data: 2642 + 56
            epochs: 15
            mainly used for the rookie arena

            t21
            base: cnocr-v2.2-densenet_lite_136-gru.ckpt
            training data: 3002 + 56
            epochs: 15
            mainly used for the rookie arena
        """
        return NikkeOcr(rec_model_name='densenet_lite_136-gru', root='./bin/cnocr_models/nikke',
                        model_name='/t21.ckpt', name='nikke')

    @cached_property
    def nikke_digit(self):
        return NikkeOcr(rec_model_name='densenet_lite_136-gru', root='./bin/cnocr_models/nikke',
                        model_name='/t21.ckpt', name='nikke_digit', cand_alphabet='0123456789')

    @cached_property
    def nikke_counter(self):
        return NikkeOcr(rec_model_name='densenet_lite_136-gru', root='./bin/cnocr_models/nikke',
                        model_name='/t21.ckpt', name='nikke_counter', cand_alphabet='0123456789/IDS')

    # @cached_property
    # def rank(self):
    #     return NikkeOcr(rec_model_name='densenet_lite_136-gru', root='./bin/cnocr_models/nikke',
    #                     model_name='/rank_t2.ckpt', name='cnocr')

    @cached_property
    def cnocr(self):
        return NikkeOcr(rec_model_name='densenet_lite_136-fc', root='./bin/cnocr_models/cnocr',
                        model_name='/cnocr-v2.2-densenet_lite_136-fc.ckpt', name='cnocr')

    @cached_property
    def cnocr_gru(self):
        return NikkeOcr(rec_model_name='densenet_lite_136-gru', root='./bin/cnocr_models/cnocr',
                        model_name='/cnocr-v2.2-densenet_lite_136-gru.ckpt', name='cnocr')

    def get_location(self, text, result):

        if result:
            if '_' in text:
                text = text.strip('_')
                r = [i['position'] for i in result if text == i['text']]
            else:
                r = [i['position'] for i in result if text in i['text']]

            if r:
                upper_left, bottom_right = r[0][0], r[0][2]
                x, y = (np.array(upper_left) + np.array(bottom_right)) / 2
                return x, y


OCR_MODEL = OcrModel()
