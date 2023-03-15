from assets import *
from common.enum.enum import *
from common.exception import Timeout
from module.base.base import BaseModule
from module.task.simulation.simulation_assets import *
from module.tools.match import matchAllTemplate
from module.tools.timer import Timer


class EffectControl(BaseModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.effect_list = []

    def get_effect_by_battle(self):
        self.device.screenshot()
        if self.device.appear(limited_2, value=0.97):
            self.skip()
            return

        if len(self.effect_list) < 8:

            current_effect_list = self.matchEffect(get_effect_list_area, add=False, _filter=True)

            timeout = Timer(15).start()
            confirm_timer = Timer(1, count=3).start()
            click_timer = Timer(1.2)

            for i in current_effect_list:
                for x in preferential_effect_list:
                    if x['name'] in i['name']:
                        quality = i['quality']
                        name = i['name']
                        user = i['user']
                        x, y = int(i['x']), int(i['y'])

                        self.INFO(f'choose effect: {name}')

                        effect_info = {
                            'quality': quality,
                            'name': name,
                            'user': user,
                            'x': x,
                            'y': y,
                        }
                        timeout.reset()
                        confirm_timer.reset()
                        click_timer.reset()

                        self.device.uiautomator_click(x, y)

                        while 1:
                            self.device.screenshot()

                            if click_timer.reached() and self.device.appear(get_effect_sign):
                                self.device.uiautomator_click(x, y)
                                confirm_timer.reset()

                            # 持有效果到底上限
                            if self.device.appear(limited):
                                self.skip()
                                return

                            # 在替换相同效果
                            if self.device.appear(replacement):
                                self.skip()
                                return

                            if click_timer.reached() and self.device.appear_then_click(confirm):
                                timeout.reset()
                                confirm_timer.reset()
                                click_timer.reset()
                                continue

                            if self.device.appear(reset_time) or self.device.appear(simulation_sign):
                                if confirm_timer.reached():
                                    self.effect_list.append(effect_info)
                                    return

                            if timeout.reached():
                                self.ERROR('wait too long')
                                raise Timeout

            self.skip()

        self.skip()

    def matchEffect(self, area, add=True, _filter=False):
        current_effect_list = []
        quality_locations = []
        text_result = self.device.textStrategy(None, area, OcrResult.ALL_RESULT,
                                               resized_shape=(2000, 2000))
        matchAllTemplate(self.device.image, [R, SR, SSR, EPIC], img_template=area, value=0.92,
                         gray=True,
                         relative_locations=quality_locations, max_count=3, min_count=3)

        text_result = list(map(lambda x: (x['text'], x['position']), text_result))

        template_left = area['area'][0]
        template_top = area['area'][1]

        for i in text_result:
            left, right = i[1][0][0] + template_left, i[1][2][0] + template_left
            top, bottom = i[1][0][1] + template_top, i[1][2][1] + template_top

            for q in quality_locations:
                if 45 >= bottom - q['bottom'] >= 15 and 45 >= top - q['top'] >= 15 and 130 >= left - q['left'] >= 115:

                    name = i[0]
                    quality = q['id']

                    x = (right - left) / 2 + left
                    y = (bottom - top) / 2 + top

                    p = list(filter(lambda x: x['name'] in name, preferential_effect_list))

                    name = p[0]['displayName'] if p else name
                    priority = p[0]['priority'] if p else 10
                    if not p:
                        p = list(filter(lambda x: x['name'] in name, useless_effect_list))
                        name = p[0]['displayName'] if p else name

                    effect_info = {
                        'quality': quality,
                        'name': name,
                        'user': None,
                        'priority': priority,
                        'x': int(x),
                        'y': int(y),
                    }

                    # same = list(
                    #     filter(lambda x: x['name'] == name, self.effect_list))
                    #
                    # if not same and add:
                    #     self.effect_list.append(effect_info)

                    # if filter:
                    #     if not same:
                    #         current_effect_list.append(effect_info)
                    # else:
                    #     current_effect_list.append(effect_info)

                    current_effect_list.append(effect_info)

                    break

        if not current_effect_list:
            x, y = quality_locations[0]['location']
            quality = quality_locations[0]['id']

            effect_info = {
                'quality': quality,
                'name': 'None',
                'user': None,
                'priority': 10,
                'x': int(x),
                'y': int(y),
            }

            current_effect_list.append(effect_info)

        return current_effect_list

    def getPreferentialEffect(self):
        self.device.drag(360, 570, 360, 890, 0.2)
        self.device.sleep(1)
        self.device.drag(360, 670, 360, 645, 0.2)
        self.device.sleep(1)
        self.device.screenshot()
        current_effect_list = self.matchEffect(own_effect_list_area, add=False)
        current_effect_list.sort(key=lambda x: x['priority'])

        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        x, y = current_effect_list[0]['x'], current_effect_list[0]['y']

        self.device.uiautomator_click(x, y)

        while 1:
            self.device.screenshot()
            if click_timer.reached() and self.device.appear(need_to_improve) or self.device.appear(need_to_choose):
                self.device.uiautomator_click(x, y)
                timeout.reset()
                confirm_timer.reset()

            if click_timer.reached() and self.device.appear_then_click(confirm):
                timeout.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(reset_time):
                if confirm_timer.reached():
                    # 更改升级后的效果
                    # self.effect_list = [{**i, 'quality': new['quality']}
                    #                     if i['name'] == new['name'] and i['user'] == new['user']
                    #                     else i
                    #                     for i in self.effect_list]
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def skip(self):
        print('skip')
        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=4).start()
        click_timer = Timer(1.2)

        import numpy as np
        import cv2

        # cancel 为不相交X号
        # cancel_2 为相交X号

        # 在替换界面为 cancel_2

        mask = np.zeros(self.device.image.shape[:2], np.uint8)

        while 1:
            self.device.screenshot()

            if click_timer.reached() \
                    and self.device.hide(confirm, img_template=effect_option_area_middle) \
                    and self.device.appear_then_click(cancel, img_template=effect_option_area_bottom):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()

                p = cancel['area']

                click_timer.wait()
                self.device.screenshot()

                left = p[0]
                right = p[2]
                top = p[1]
                bottom = p[3]

                mask[top:bottom, left:right] = 255
                self.device.image = cv2.bitwise_and(self.device.image, self.device.image, mask=cv2.bitwise_not(mask))

            if click_timer.reached() \
                    and self.device.hide(cancel, img_template=effect_option_area_bottom) \
                    and self.device.appear_then_click(cancel_2, img_template=effect_option_area_bottom):
                click_timer.wait()
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()

            if click_timer.reached() and self.device.appear_then_click(confirm,
                                                                       img_template=effect_option_area_middle):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()

            if self.device.appear(reset_time) or self.device.appear(end_simulation):
                if confirm_timer.reached():
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout


preferential_effect_list = [
    {
        'displayName': '高品质粉末',
        'name': '高品质',
        'priority': 1

    },
    {
        'displayName': '超越弹匣',
        'name': '超越',
        'priority': 1

    },
    {
        'displayName': '快速弹匣',
        'name': '速弹',
        'priority': 1

    },
    {
        'displayName': '反射弹头',
        'name': '反射',
        'priority': 2

    },
    {
        'displayName': '控制引导器',
        'name': '引导',
        'priority': 2

    },
    {
        'displayName': '艾薇拉粒子干扰丝',
        'name': '干扰丝',
        'priority': 2

    },
    {
        'displayName': '快速充电器',
        'name': '充电',
        'priority': 3

    },
    {
        'displayName': '冲击引流器',
        'name': '冲击',
        'priority': 3

    },
    {
        'displayName': '隐身粉',
        'name': '隐身粉',
        'priority': 3

    },
    {
        'displayName': '聚焦瞄准镜',
        'name': '瞄准',
        'priority': 3

    },
    {
        'displayName': '连结AMO',
        'name': '连结',
        'priority': 4

    },
    {
        'displayName': '连结AMO',
        'name': 'AMO',
        'priority': 4

    },
    {
        'displayName': '引流转换器',
        'name': '引流',
        'priority': 5

    },
    {
        'displayName': '恢复模组',
        'name': '恢复',
        'priority': 6

    },
    {
        'displayName': '小型离子束屏障',
        'name': '离子',
        'priority': 6

    },
    {
        'displayName': '辅助发电机',
        'name': '发电',
        'priority': 10

    },
    {
        'displayName': '自动对焦眼球',
        'name': '对焦',
        'priority': 10

    },
    {
        'displayName': '重启载体',
        'name': '重启',
        'priority': 10

    },
    {
        'displayName': '快速换弹程序',
        'name': '速换',
        'priority': 10

    },
]

useless_effect_list = [
    {
        'displayName': '小型离子束屏障',
        'name': '离子',
        'priority': 6

    },
    {
        'displayName': '辅助发电机',
        'name': '发电',
        'priority': 10

    },
    {
        'displayName': '自动对焦眼球',
        'name': '对焦',
        'priority': 10

    },
    {
        'displayName': '重启载体',
        'name': '重启',
        'priority': 10

    },
    {
        'displayName': '快速换弹程序',
        'name': '速换',
        'priority': 10

    },
]
