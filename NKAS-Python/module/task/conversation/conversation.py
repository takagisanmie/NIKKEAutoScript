import re
from common.enum.enum import *
from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI
from _conversation import Nikke_list, Nikke_dialog
from module.task.conversation.conversation_assets import *


class Conversation(UI, Task):
    def run(self):
        self.LINE('Conversation')
        # 选择的中nikke列表
        self.go(page_conversation_list)
        self.checkRestChance()
        selected_list = self.config.get('Task.Conversation.nikkeList', self.config.task_dict)
        _Nikke_list = list(filter(lambda x: x["key"] in selected_list, Nikke_list))
        company_list = [Elysion, Missilis, Tetra, Pilgrim, Abnormal]
        if self.rest_chance == 0:
            self._finish()
            return
        self.chooseNikke(_Nikke_list, company_list)

        self._finish()

    def _finish(self):
        self.finish(self.config, 'Conversation')
        self.INFO('Conversation is finished')
        self.go(page_main)

    def checkRestChance(self):
        self.device.sleep(0.3)
        self.device.screenshot()
        self.rest_chance = self.device.textStrategy(None, rest_chance, OcrResult.TEXT)
        self.rest_chance = int(self.rest_chance.split('/')[0])
        if self.rest_chance > 0:
            self.INFO(f'rest chance: {self.rest_chance}')
            return True
        else:
            self.INFO('Conversation has no chance')

    def chooseNikke(self, _Nikke_list, company_list):
        print('chooseNikke')

        timeout = Timer(60).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        company = company_list[0]
        flag = True

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(company):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                self.device.sleep(2.5)
                continue

            if flag and self.device.hide(company):
                flag = False
                company_list = company_list[1:]

            for index, value in enumerate(_Nikke_list):

                p = self.device.textStrategy(value['label'], name_list, OcrResult.POSITION)

                if p is not None:

                    template_left = name_list['area'][0]
                    template_top = name_list['area'][1]

                    left, right = p[0][0] + template_left, p[2][0] + template_left
                    top, bottom = p[0][1] + template_top, p[2][1] + template_top

                    # upper_left, bottom_right = p[0], p[2]
                    # left top right bottom

                    position = [left, top, right, bottom]

                    sl = self.device.matchRelative(position, 500, 520, 15, 40, case_closed, 0.8,
                                                   ImgResult.SIMILARITY)

                    if not sl:
                        self.INFO(f'wait to communicate: {value["label"]}')
                        self.communicate(value['key'], value['label'])
                        _Nikke_list.remove(value)
                        timeout.reset()
                        confirm_timer.reset()
                        click_timer.reset()

                        self.rest_chance -= 1
                        if self.rest_chance == 0:
                            return
                    else:
                        self.WARNING(f'already communicated: {value["label"]}')
                        _Nikke_list.remove(value)
                        confirm_timer.reset()

            if confirm_timer.reached():
                if len(company_list) > 0 and self.rest_chance > 0:
                    self.device.swipe(300, 1020, 300, 640, 0.2)
                    self.device.sleep(1.2)
                    timeout.reset()
                    confirm_timer.reset()
                    click_timer.reset()
                    continue
                else:
                    return

            if self.device._hide(favourite):
                if len(company_list) > 0 and self.rest_chance > 0:
                    return self.chooseNikke(_Nikke_list, company_list)
                else:
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def communicate(self, key, name):

        timeout = Timer(30).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        flag = True

        while 1:
            self.device.screenshot()

            if flag and click_timer.reached() \
                    and self.device.hide(conversation_detail_sign) \
                    and self.device.hide(auto) \
                    and self.device.clickTextLocation(name):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.appear(conversation_detail_sign) and self.device.appear(
                    level_max) and self.device.appear_then_click(back):
                flag = False
                self.device.sleep(2)
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if flag and click_timer.reached() and self.device.appear_then_click(confirm, img_template=middle):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if flag and click_timer.reached() and self.device.appear_then_click(start_conversation):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if flag and click_timer.reached() and self.device.appear(option):
                flag = False
                self.chooseAnswer(key, name)
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() \
                    and self.device.appear(auto) \
                    and self.device.multiClickLocation((200, 200), 4, 0.1):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.appear(conversation_list_sign):
                if confirm_timer.reached():
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def chooseAnswer(self, key, name):
        import cv2
        import time

        timeout = Timer(30).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        answer_list = Nikke_dialog[key]
        resized_shape = [(3000, 3000), (768, 768)]

        flag = True
        match = True

        while 1:
            self.device.screenshot()

            if match and click_timer.reached() and self.device.appear(option):

                match = False

                for shape in resized_shape:
                    if answer1 := self.device.textStrategy(None, answer_area_1, OcrResult.TEXT, resized_shape=shape):
                        answer1 = self.removePunctuation(answer1)
                    if answer2 := self.device.textStrategy(None, answer_area_2, OcrResult.TEXT, resized_shape=shape):
                        answer2 = self.removePunctuation(answer2)

                    for text in answer_list:
                        if answer1 is not None and text in answer1:
                            self.device.multiClickLocation((340, 860), 2, 0.2)
                            self.INFO(f'Love and affection point with {key} + 100')
                            flag = False
                            break

                        elif answer2 is not None and text in answer2:
                            self.device.multiClickLocation((340, 960), 2, 0.2)
                            self.INFO(f'Love and affection point with {key} + 100')
                            flag = False
                            break

                    if not flag:
                        break

            if flag:
                flag = False
                self.device.screenshot()
                cv2.imwrite(f'./pic/answer-{key}-{time.time()}.png', self.device.image)
                self.WARNING(f'{name} No correct answer was found.')
                self.WARNING('NKAS has saved the screenshot and the path is "./pic".')
                self.WARNING(f'Love and affection point with {key} + 50')

            if click_timer.reached() \
                    and self.device.appear(auto) \
                    and self.device.multiClickLocation((340, 860), 2, 0.2):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(level_up_confirm):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() \
                    and self.device.appear(conversation_deatil_sign_2, gray=True) \
                    and self.device.appear_then_click(back):
                self.device.sleep(2)
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                click_timer.wait()
                click_timer.reset()
                continue

            if self.device.appear(conversation_list_sign):
                if confirm_timer.reached():
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def removePunctuation(self, text):
        return re.sub(r'[\W]', '', text)
