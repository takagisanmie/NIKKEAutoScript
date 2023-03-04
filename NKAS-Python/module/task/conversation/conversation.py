import re

import assets
from common.enum.enum import *
from module.base.task import Task
from module.ui.page import *
from module.ui.ui import UI
from _conversation import Nikke_list, Nikke_dialog


class Conversation(UI, Task):
    def run(self):
        self.LINE('Conversation')
        self.go(destination=page_conversation_list)
        self.device.screenshot()
        self.checkRestChance()
        # 未咨询nikke列表
        _list = self.getNikkeList()

        _list = _list[:self.restChance]

        if len(_list) > 0:
            for nikke in _list:
                self.device.clickTextLocation(nikke['label'], AssetResponse.ASSET_SHOW, True,
                                              assets.in_conversation_detail_sign)

                if self.device.isVisible(assets.in_conversation_detail_max):
                    self.device.click(assets.back, AssetResponse.ASSET_SHOW, assets.in_conversation_list_sign)
                    self.INFO(f'Love and affection point with {nikke["label"]} are max')
                    continue

                self.device.click(assets.in_conversation_detail_start_conversation, AssetResponse.ASSET_HIDE)
                self.device.click(assets.confirm, AssetResponse.ASSET_SHOW,
                                  assets.in_conversation_detai_in_talking_cancel)
                self.device.multiClickLocation((150, 50), 2, AssetResponse.ASSET_SHOW, assets.dialog_box)
                self.chooseAnswer(nikke)
                self.device.multiClickLocation((950, 730), 2, AssetResponse.ASSET_SHOW, assets.back)
                self.device.sleep(3.5)
                self.appear_then_click(assets.confirm2, AssetResponse.ASSET_HIDE, True)
                self.device.click(assets.back, AssetResponse.ASSET_SHOW, assets.in_conversation_list_sign)
                continue

        self.device.click(assets.home, AssetResponse.ASSET_HIDE)
        self.finish(self.config, 'Conversation')
        self.INFO('Conversation is finished')

    def checkRestChance(self):
        self.restChance = self.device.textStrategy(None, assets.in_conversation_list_rest_number, OcrResult.TEXT)
        self.restChance = int(self.restChance.split('/')[0])
        if self.restChance > 0:
            self.INFO(f'rest chance: {self.restChance}')
            return True
        else:
            self.INFO('Conversation has no chance')

    def getNikkeList(self):
        _list = []
        # 选择的中nikke列表
        selected_list = self.config.get('Task.Conversation.nikkeList', self.config.Task_Dict)
        for name in selected_list:
            nikke = list(filter(lambda n: n['key'] == name, Nikke_list))[0]
            # 获取名字位置
            p = self.device.textStrategy(nikke['label'], None, OcrResult.POSITION)
            try:
                if p.all():
                    upper_left, bottom_right = p[0], p[2]
                    position = [int(upper_left[0]), int(upper_left[1]), int(bottom_right[0]), int(bottom_right[1])]
                    # 匹配相对名字位置的已咨询标识
                    sl = self.device.matchRelative(position, 420, 500, 10, 40, assets.case_closed, 0.8,
                                                   ImgResult.SIMILARITY)
                    # 将未匹配到nikke加入列表
                    if sl is None:
                        self.INFO(f'wait to communicate: {name}')
                        _list.append({'name': name, 'label': nikke['label']})

            except Exception as e:
                self.ERROR(f'{nikke["label"]}: no data was found')

        return _list

    def chooseAnswer(self, nikke):
        import cv2
        import time

        # 回答
        self.device.screenshot()
        resized_shape = [(3000, 3000), (768, 768)]
        for shape in resized_shape:
            if answer1 := self.device.textStrategy(None, assets.answer1, OcrResult.TEXT, resized_shape=shape):
                answer1 = self.removePunctuation(answer1)
            if answer2 := self.device.textStrategy(None, assets.answer2, OcrResult.TEXT, resized_shape=shape):
                answer2 = self.removePunctuation(answer2)
            for text in Nikke_dialog[nikke['name']]:
                if answer1 is not None and text in answer1:
                    self.INFO(f'Love and affection point with {nikke["name"]} + 100')
                    self.device.clickLocation((950, 730), AssetResponse.ASSET_HIDE,
                                              assets.in_conversation_detai_in_talking_cancel)
                    return True

                elif answer2 is not None and text in answer2:
                    self.INFO(f'Love and affection point with {nikke["name"]} + 100')
                    self.device.clickLocation((950, 820), AssetResponse.ASSET_HIDE,
                                              assets.in_conversation_detai_in_talking_cancel)
                    return True

        self.device.screenshot()
        cv2.imwrite(f'./pic/answer-{time.time()}.png', self.device.image)
        self.INFO(f'{nikke} No correct answer was found.')
        self.INFO('NKAS has saved the screenshot and the path is "./pic".')
        self.INFO(f'Love and affection point with {nikke["name"]} + 50')

        self.device.clickLocation((950, 730), AssetResponse.ASSET_HIDE, assets.in_conversation_detai_in_talking_cancel)
        return True

    def removePunctuation(self, text):
        return re.sub(r'[\W]', '', text)
