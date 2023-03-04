from functools import cached_property

import assets
from module.base.task import Task
from module.tools.match import match
from module.ui.ui import UI
from module.ui.page import *
from common.enum.enum import AssetResponse, EventParameter, ImgResult, OcrResult, Path


class Event(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        history = self.config.get('Task.Event.historyEvent', self.config.Task_Dict)
        currentEvent = self.config.get('Task.Event.currentEvent', self.config.Task_Dict)
        e = list(filter(lambda x: x["value"] == currentEvent, history))[0]
        self.type = e['type']
        self.path = e['path']
        self.part = self.config.get('Task.Event.part', self.config.Task_Dict)
        self.step = int(self.config.get('Task.Event.step', self.config.Task_Dict).split('-')[1])
        self.difficulty = self.config.get('Task.Event.difficulty', self.config.Task_Dict)
        self.finishAllSteps = self.config.get('Task.Event.finishAllSteps', self.config.Task_Dict)

    def run(self):
        self.LINE('Event')
        self.go(destination=page_main)

        if self.device.isHidden(self.assets.page_main_button):
            self.INFO('当前活动已经结束')
            self._finish()
            return

        print(self.pages)
        # 路径
        # 小活动只有part1
        if self.type == EventParameter.SMALL:
            self._go(destination=self.assets.event_part1)
            self.checkRestChance()
            self.device.click(self.assets.event_part1_to_steps, AssetResponse.ASSET_SHOW,
                              self.assets.event_part1_steps_sign)

        # 大活动有part1、part2
        elif self.type == EventParameter.LARGE:
            if self.part == EventParameter.PART_1:
                self._go(destination=self.assets.event_part1)
                self.checkRestChance()
                self.device.click(self.assets.event_part1_to_steps, AssetResponse.ASSET_SHOW,
                                  self.assets.event_part1_steps_sign)

            elif self.part == EventParameter.PART_2:
                self._go(destination=self.assets.event_part2)
                self.checkRestChance()
                self.device.click(self.assets.event_part2_to_steps, AssetResponse.ASSET_SHOW,
                                  self.assets.event_part2_steps_sign)

        if self.chance == 0:
            self._finish()
            return

        self.change_part_difficulty()

        if self.finishAllSteps:
            self.finishAllStep()

        self.loop()

        self._finish()

    def loop(self):
        self.srollToTop()
        part_A = self.checkState(self.part_A, self.part_finished_template)
        count_A = len(part_A)
        if count_A >= self.step:
            lc = part_A[self.step - 1]
            self.device.clickLocation(lc, AssetResponse.ASSET_SHOW, assets.into_battle3)
            self.device.click(assets.into_battle3, AssetResponse.ASSET_HIDE)
        else:
            self.step -= count_A
            self.srollToBottom()
            part_B = self.checkState(self.part_B, self.part_finished_template)
            count_B = len(part_B)
            if count_B >= self.step:
                lc = part_B[self.step - 1]
                self.device.clickLocation(lc, AssetResponse.ASSET_SHOW, assets.into_battle3)
                self.device.click(assets.into_battle3, AssetResponse.ASSET_HIDE)
            else:
                self.socket.ERROR('关卡填写错误')
                return

        self.chance -= 1

        # 通过重新开始完成
        while 1:
            self.device.wait(assets.end_battle3)
            if lc := match(self.device.image, assets.event_restart, 0.92, ImgResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.ASSET_HIDE, assets.event_restart)
                self.chance -= 1

            if self.chance == 0:
                self.device.clickLocation((300, 300), AssetResponse.ASSET_SHOW, assets.home)
                return

    def _finish(self):
        self.device.click(assets.home, AssetResponse.ASSET_HIDE)
        self.INFO('Event has no chance')
        self.finish(self.config, 'Event')
        self.INFO('Event is finished')

    def checkRestChance(self):
        self.chance = self.device.textStrategy(None, assets.event_chance, OcrResult.TEXT)
        self.chance = int(self.chance.split('/')[0])
        pass

    def finishAllStep(self):
        self.srollToTop()
        self.checkPart(self.part_A, self.part_template)
        self.srollToBottom()
        self.checkPart(self.part_B, self.part_template)

    def checkPart(self, part, temp):
        locations = self.checkState(part, temp)
        available_count = len(locations)

        if available_count == 0 or self.chance == 0:
            if part is self.part_B and available_count == 0:
                self.config.update('Task.Event.finishAllSteps', False, self.config.Task_Dict, Path.TASK)
            return

        while 1:
            self.device.screenshot()

            if lc := match(self.device.image, temp, 0.92, ImgResult.LOCATION, gray=True):
                self.device.clickLocation(lc, AssetResponse.ASSET_SHOW, assets.into_battle3)
                self.device.click(assets.into_battle3, AssetResponse.ASSET_HIDE)

            if lc := match(self.device.image, assets.skip, 0.84, ImgResult.LOCATION):
                self.device.clickLocation(lc, AssetResponse.ASSET_HIDE, assets.skip)

            if match(self.device.image, assets.end_battle3, 0.84, ImgResult.LOCATION):
                while 1:
                    if lc := match(self.device.image, assets.skip, 0.84, ImgResult.LOCATION):
                        self.device.clickLocation(lc, AssetResponse.ASSET_HIDE, assets.skip)

                    self.device.clickLocation((300, 300), AssetResponse.NONE)

                    if self.device.isVisible(assets.home):
                        break

                available_count -= 1
                self.chance -= 1

            if available_count == 0 or self.chance == 0:
                return

            self.device.sleep(1)

    def change_part_difficulty(self):
        normal = None
        hard = None
        if self.type == EventParameter.SMALL:

            normal = self.assets.part1_difficulty_normal
            hard = self.assets.part1_difficulty_hard

            if self.difficulty == EventParameter.NORMAL:
                self.part_A = self.assets.part1_normal_A
                self.part_B = self.assets.part1_normal_B
                self.part_template = self.assets.part1_normal
                self.part_locked_template = self.assets.part1_normal_locked
                self.part_finished_template = self.assets.part1_normal_finished

            elif self.difficulty == EventParameter.HARD:
                self.part_A = self.assets.part1_hard_A
                self.part_B = self.assets.part1_hard_B
                self.part_template = self.assets.part1_hard
                self.part_locked_template = self.assets.part1_hard_locked
                self.part_finished_template = self.assets.part1_hard_finished


        elif self.type == EventParameter.LARGE:

            if self.part == EventParameter.PART_1:

                normal = self.assets.part1_difficulty_normal
                hard = None

                if self.difficulty == EventParameter.NORMAL:
                    self.part_A = self.assets.part1_normal_A
                    self.part_B = self.assets.part1_normal_B
                    self.part_template = self.assets.part1_normal
                    self.part_locked_template = self.assets.part1_normal_locked
                    self.part_finished_template = self.assets.part1_normal_finished

            elif self.part == EventParameter.PART_2:

                normal = self.assets.part2_difficulty_normal
                hard = self.assets.part2_difficulty_hard

                if self.difficulty == EventParameter.NORMAL:
                    self.part_A = self.assets.part2_normal_A
                    self.part_B = self.assets.part2_normal_B
                    self.part_template = self.assets.part2_normal
                    self.part_locked_template = self.assets.part2_normal_locked
                    self.part_finished_template = self.assets.part2_normal_finished

                elif self.difficulty == EventParameter.HARD:
                    self.part_A = self.assets.part2_hard_A
                    self.part_B = self.assets.part2_hard_B
                    self.part_template = self.assets.part2_hard
                    self.part_locked_template = self.assets.part2_hard_locked
                    self.part_finished_template = self.assets.part2_hard_finished

        if self.difficulty == EventParameter.NORMAL:
            self.changeDifficulty(normal)

        elif self.difficulty == EventParameter.HARD:
            try:
                self.changeDifficulty(hard)

            except Exception as e:
                self.ERROR('难度选择错误')
                self.getErrorInfo()

    def changeDifficulty(self, asset):
        position = asset['area']
        lc = (((position[2] - position[0]) / 2 + position[0]), ((position[3] - position[1]) / 2 + position[1]))
        self.device.multiClickLocation(lc, 2, AssetResponse.NONE)
        pass

    def checkState(self, part, template):
        import cv2
        import numpy as np

        self.device.screenshot()
        p = part['area']
        img = self.device.image[p[1]:p[3], p[0]:p[2]]
        width = p[0]
        height = p[1]
        p = template['area']
        template = cv2.imread(template['path'])[p[1]:p[3], p[0]:p[2]]
        h, w, c = template.shape
        mask = np.zeros(img.shape[:2], np.uint8)
        relative_locations = []
        while 1:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            _, sl, _, upper_left = cv2.minMaxLoc(result)
            sl = round(sl, 2)
            if sl < 0.9:
                break

            else:
                bottom_right = (upper_left[0] + w, upper_left[1] + h)
                position = (upper_left[0], upper_left[1], bottom_right[0], bottom_right[1])
                lc = (((position[2] - position[0]) / 2 + position[0]), ((position[3] - position[1]) / 2 + position[1]))
                x, y = int(lc[0]), int(lc[1])
                # cv2.putText(img, str(count + 1), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (111, 255, 0), 2, cv2.LINE_AA)
                mask[y:y + h, x:x + w] = 255
                img = cv2.bitwise_and(img, img, mask=cv2.bitwise_not(mask))  # 去除已经匹配到的标识
                # relative_locations.append((lc, (x + w // 2, y + h // 2)))
                x += width
                y += height
                relative_locations.append((int(x + w // 2), int(y + h // 2)))

        # relative_locations.sort(key=lambda x: (x[1][1], x[1][0]))
        if len(relative_locations) > 0:
            relative_locations.sort(key=lambda x: x[1])

        return relative_locations

    def srollToTop(self):
        for i in range(2):
            self.device.swipe(960, 400, 960, 760, 0.2)
            self.device.sleep(0.6)
        pass

    def srollToBottom(self):
        for i in range(2):
            self.device.swipe(960, 760, 960, 400, 0.2)
            self.device.sleep(0.6)

    @cached_property
    def assets(self):
        from module.task.event.e_assets import EventAssets
        from module.task.event.generateAssets import generateTemplate, generateAssets
        e = EventAssets()
        generateTemplate(f'./module/task/event/templates{self.path}')
        generateAssets(assets=e)
        return e

    @cached_property
    def pages(self):
        from module.ui.page import Page, page_main
        event_page_main = Page(signs=[self.assets.event_page_main_sign], name='event_page_main', parent=page_main)
        event_page_main.link(button=assets.home, destination=page_main)
        event_page_main.link(button=assets.back, destination=page_main)

        event_part1 = Page(signs=[self.assets.event_part1_sign], name='event_part1', parent=event_page_main)
        event_part1.link(button=assets.home, destination=page_main)
        event_part1.link(button=assets.back, destination=event_page_main)

        event_page_main.link(button=self.assets.event_page_main_to_part1, destination=event_part1)

        event_part1_steps = Page(signs=[self.assets.event_part1_steps_sign], name='event_part1_steps',
                                 parent=event_part1)

        event_part1_steps.link(button=assets.home, destination=page_main)
        event_part1_steps.link(button=assets.back, destination=event_part1)

        event_part1.link(button=self.assets.event_part1_to_steps, destination=event_part1_steps)

        event_part2 = Page(signs=[self.assets.event_part2_sign], name='event_part2', parent=event_page_main)
        event_part2.link(button=assets.home, destination=page_main)
        event_part2.link(button=assets.back, destination=event_page_main)

        event_page_main.link(button=self.assets.event_page_main_to_part2, destination=event_part2)

        event_part2_steps = Page(signs=[self.assets.event_part2_steps_sign], name='event_part2_steps',
                                 parent=event_part2)

        event_part2_steps.link(button=assets.home, destination=page_main)
        event_part2_steps.link(button=assets.back, destination=event_part2)

        event_part2.link(button=self.assets.event_part2_to_steps, destination=event_part2_steps)

        if self.type == EventParameter.SMALL:
            page_main.link(button=self.assets.page_main_button, destination=event_part1)
        elif self.type == EventParameter.LARGE:
            page_main.link(button=self.assets.page_main_button, destination=event_page_main)

        self.assets.event_page_main = event_page_main
        self.assets.event_part1 = event_part1
        self.assets.event_part1_steps = event_part1_steps
        self.assets.event_part2 = event_part2
        self.assets.event_part2_steps = event_part2_steps

        return [event_page_main, event_part1]

    def _go(self, destination):
        path1 = []
        self.getPathByBack(path1, UI.current_page)
        path2 = []
        self.getPathByParent(path2, destination)
        for a_index, a_value in enumerate(path1):
            for b_index, b_value in enumerate(path2):
                if a_value['destination'].name == b_value['destination'].name:
                    path1 = path1[b_index:a_index + 1]
                    path2 = path2[b_index + 1:len(path2)]

        path = path1 + path2
        self.go_to_destination(path)
        pass
