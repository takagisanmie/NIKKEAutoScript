import functools

import assets
import glo
from common.enum.enum import *


def response(origin):
    @functools.wraps(origin)
    def prefix(*args, **kwargs):
        # TODO 超时
        # sleep_time = 0.45
        sleep_time = 0.1
        limit = 6
        while 1:
            res = origin(*args, **kwargs)
            if origin.__name__ == 'click':
                control, button, then = res[0], res[1], res[2]
                if then == AssetResponse.ASSET_HIDE:
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.isHidden(button):
                            return res

                if then == AssetResponse.ASSET_SHOW:
                    asset = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.isVisible(asset):
                            return res
                        elif control.isHidden(button) and control.isVisible(assets.in_loading):
                            while 1:
                                control.screenshot()
                                if control.isVisible(asset):
                                    return res

                if then == AssetResponse.TEXT_SHOW:
                    show_text = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.textStrategy(show_text, None, OcrResult.TEXT):
                            return res

                if then == AssetResponse.TEXT_HIDE:
                    hide_text = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.textStrategy(hide_text, None, OcrResult.TEXT) is None:
                            return res
                        else:
                            control.clickTextLocation(hide_text, AssetResponse.NONE)

                if then == AssetResponse.NONE:
                    return res

            if origin.__name__ == 'clickLocation':
                control, location, then = res[0], res[1], res[2]

                if then == AssetResponse.ASSET_HIDE:
                    button = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.isHidden(button):
                            return res

                if then == AssetResponse.ASSET_SHOW:
                    asset = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.isVisible(asset):
                            return res

                if then == AssetResponse.TEXT_SHOW:
                    show_text = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.textStrategy(show_text, None, OcrResult.TEXT):
                            return res

                if then == AssetResponse.TEXT_HIDE:
                    hide_text = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.textStrategy(hide_text, None, OcrResult.TEXT) is None:
                            return res
                        else:
                            control.clickTextLocation(hide_text, AssetResponse.NONE)

                if then == AssetResponse.NONE:
                    return res

            if origin.__name__ == 'clickTextLocation':
                control, text, then = res[0], res[1], res[2]

                if then == AssetResponse.ASSET_SHOW:
                    asset = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.isVisible(asset):
                            return res

                if then == AssetResponse.TEXT_SHOW:
                    show_text = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.textStrategy(show_text, None, OcrResult.TEXT):
                            return res

                if then == AssetResponse.TEXT_HIDE:
                    hide_text = res[3]
                    for i in range(limit):
                        control.sleep(sleep_time)
                        control.screenshot()
                        if control.textStrategy(hide_text, None, OcrResult.TEXT) is None:
                            return res
                        else:
                            control.clickTextLocation(hide_text, AssetResponse.NONE)

                if then == AssetResponse.PAGE_CHANGE:
                    control.screenshot()
                    current_page = glo.getNKAS().ui.where()
                    destination = res[3]
                    if current_page is destination:
                        return res

                if then == AssetResponse.NONE:
                    return res

    return prefix
