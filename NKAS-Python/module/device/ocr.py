from cnocr import CnOcr

from common.enum.enum import OcrResult

cnOcr = CnOcr()


class Ocr:
    def _ocr(self, img, text=None, _result=None, line=False, *args, **kwargs):
        if not line:
            res = cnOcr.ocr(img, **kwargs)
            result = self.filterText(text, res, _result)
            if result is not None:
                return result
            else:
                return None
        elif line:
            res = cnOcr.ocr_for_single_line(img)
            print(res)
            if res is not None:
                return res['text']
            else:
                return None

    def _ocrByAsset(self, img, text, asset=None, _result=None, line=None, screenshot=False, *args, **kwargs):
        if asset is not None:
            p = asset['area']
            img = img[p[1]:p[3], p[0]:p[2]]

        if not line:
            res = cnOcr.ocr(img, **kwargs)
            result = self.filterText(text, res, _result, asset)
            if result is not None:
                return result
            else:
                return None
        elif line:
            res = cnOcr.ocr_for_single_line(img)
            if res is not None:
                return res['text']
            else:
                return None

    def filterText(self, text, res, _result, asset=None):
        if text is None:
            text = 'None'

        if len(res) > 0:
            if '_' in text:
                text = text.split('_')[1]
                for t in filter(lambda r: text == r['text'], res):
                    text = t['text']

                    lc = self.getLocation(t, asset)
                    if _result is OcrResult.LOCATION:
                        return lc
                    if _result is OcrResult.TEXT:
                        return text
                    if _result is OcrResult.LOCATION_AND_TEXT:
                        return lc, text
                    if _result is OcrResult.POSITION:
                        return t['position']
                    if _result is OcrResult.LOCATION_AND_POSITION:
                        return lc, t['position']
            else:
                for t in filter(lambda r: text in r['text'], res):
                    text = t['text']
                    lc = self.getLocation(t, asset)
                    if _result is OcrResult.LOCATION:
                        return lc
                    if _result is OcrResult.TEXT:
                        return text
                    if _result is OcrResult.LOCATION_AND_TEXT:
                        return lc, text
                    if _result is OcrResult.POSITION:
                        return t['position']
                    if _result is OcrResult.LOCATION_AND_POSITION:
                        return lc, t['position']

            # 有字符串，但没有匹配到，则返回None
            if text != 'None' and _result is OcrResult.TEXT:
                return None
            elif text != 'None' and _result is OcrResult.LOCATION_AND_TEXT:
                return None
            # 没有符合参数的文本或没有输入，且有返回结果，则返回识别的文本
            elif _result is OcrResult.TEXT:
                return res[0]['text']
            elif _result is OcrResult.LOCATION_AND_TEXT:
                lc = self.getLocation(res[0])
                return lc, res[0]['text']
            elif _result is OcrResult.ALL_RESULT:
                return res

        return None

    def getLocation(self, t, asset):
        upper_left, bottom_right = t['position'][0], t['position'][2]

        left = upper_left[0]
        right = bottom_right[0]
        top = upper_left[1]
        bottom = bottom_right[1]

        if asset:
            template_left = asset['area'][0]
            template_top = asset['area'][1]

            left += template_left
            right += template_left
            top += template_top
            bottom += template_top

        # position = (left, right, top, bottom)

        lc = (((right - left) / 2 + left), ((bottom - top) / 2 + top))
        return lc
