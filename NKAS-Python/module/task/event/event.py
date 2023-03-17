from functools import cached_property

from common.exception import Timeout
from module.base.task import Task
from module.tools.timer import Timer
from module.ui.ui import UI
from module.ui.page import *
from common.enum.enum import EP, ImgResult, OcrResult, Path


class Event(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        history = self.config.get('Task.Event.historyEvent', self.config.Task_Dict)
        currentEvent = self.config.get('Task.Event.currentEvent', self.config.Task_Dict)
        e = list(filter(lambda x: x["value"] == currentEvent, history))[0]
        self.type = e['type']
        self.path = e['path']
        self.part = self.config.get('Task.Event.part', self.config.Task_Dict)
        self.step = int(self.config.get('Task.Event.event', self.config.Task_Dict).split('-')[1])
        self.difficulty = self.config.get('Task.Event.difficulty', self.config.Task_Dict)
        self._finishAllEvent = self.config.get('Task.Event.finishAllEvent', self.config.Task_Dict)
        if self.type == EP.SMALL:
            self.part = EP.PART_1

    def run(self):
        self.LINE('Event')
        print(self.pages)
        self.go(destination=page_main)
        self.go_to_steps()

        if not self.rest_chance:
            self._finish()
            return

        self.change_part_difficulty()
        if self._finishAllEvent:
            self.finishAllEvent()

        if not self.rest_chance:
            self._finish()
            return

        self.loop()

        self._finish()

    def loop(self):
        self.sroll_to_top()
        locations_1 = self.device.appear(self.finished, img_template=self.area_1, _result=ImgResult.ALL_RESULT,
                                         screenshot=True)
        if len(locations_1) >= self.step:
            lc = locations_1[self.step - 1]['location']
        else:

            self.step -= len(locations_1)
            self.sroll_to_bottom()
            locations_2 = self.device.appear(self.finished, img_template=self.area_2, _result=ImgResult.ALL_RESULT,
                                             screenshot=True)

            lc = locations_2[self.step - 1]['location']

        timeout = Timer(60).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()
            if not self.rest_chance \
                    and self.device.appear(home) \
                    and confirm_timer.reached():
                return

            if click_timer.reached() and self.device.appear_then_click(self.assets.option):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.clickTextLocation(text='SKIP', asset=self.assets.skip_area):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear(self.assets.auto, gray=True):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                self.device.sleep(5)
                continue

            if self.rest_chance and click_timer.reached() \
                    and self.device.appear(self.assets.step_sign) \
                    and self.device._hide(self.assets.into_battle) \
                    and self.device.uiautomator_click(lc[0], lc[1]):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.rest_chance and click_timer.reached() and self.device.appear_then_click(self.assets.into_battle):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(self.assets.restart) or self.device.appear_then_click(self.assets.end_battle):
                self.rest_chance -= 1
                self.INFO(f'rest chance: {self.rest_chance}')
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def _finish(self):
        self.device.appear_then_click(home)
        self.INFO('Event has no chance')
        self.finish(self.config, 'Event')
        self.INFO('Event is finished')
        self.go(page_main)

    def finishAllEvent(self):
        self.sroll_to_top()
        timeout = Timer(60).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(self.assets.option):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.clickTextLocation(text='SKIP', asset=self.assets.skip_area):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.rest_chance and self.device.appear(self.assets.auto, gray=True):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                self.device.sleep(5)
                continue

            if click_timer.reached() and (lc := self.device.appear(self.assets.end_battle)):
                self.device.multiClickLocation(lc)
                self.rest_chance -= 1
                self.INFO(f'rest chance: {self.rest_chance}')
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.rest_chance and click_timer.reached() and self.device.appear_then_click(self.assets.into_battle):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.rest_chance and click_timer.reached() and self.device.appear_then_click(self.unlocked):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                click_timer.wait()
                continue

            if self.device.appear(home) and not self.rest_chance:
                return

            if self.device.appear(home) and self.device.swipe(360, 1000, 360, 800, 0.4):
                self.device.sleep(1)
                if confirm_timer.reached():
                    self.config.update('Task.Event.finishAllEvent', False, self.config.Task_Dict, Path.TASK)
                    return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def go_to_steps(self):
        if (self.type == EP.SMALL or self.type == EP.LARGE) and self.part == EP.PART_1:
            self._go(destination=self.part1)
        elif self.type == EP.LARGE and self.part == EP.PART_2:
            self._go(destination=self.part2)
        self.checkRestChance()
        if self.rest_chance == 0:
            return

        if self.type == EP.SMALL and self.part == EP.PART_1:
            self._go(destination=self.part1_detail)
        elif self.type == EP.LARGE and self.part == EP.PART_2:
            self._go(destination=self.part2_detail)
        else:
            self._go(destination=self.part1_detail)

        self.device.sleep(2)

    def change_part_difficulty(self):

        # 小活动 大活动 part1 普通
        if (self.type == EP.SMALL or self.type == EP.LARGE) \
                and self.part == EP.PART_1 \
                and self.difficulty == EP.NORMAL:
            self.device.multiClick(self.assets.normal, 2)
            self.unlocked = [self.assets.part1_normal_unlocked]

            if self.assets.part1_normal_unlocked_2:
                self.unlocked.append(self.assets.part1_normal_unlocked_2)
            if self.assets.part1_normal_unlocked_3:
                self.unlocked.append(self.assets.part1_normal_unlocked_3)

            self.finished = [self.assets.part1_normal_finished]

            if self.assets.part1_normal_finished_2:
                self.finished.append(self.assets.part1_normal_finished_2)
            if self.assets.part1_normal_finished_3:
                self.finished.append(self.assets.part1_normal_finished_3)

            self.area_1 = self.assets.part1_normal_area_1
            self.area_2 = self.assets.part1_normal_area_2

        # 小活动 Part1 困难
        if self.type == EP.SMALL \
                and self.part == EP.PART_1 \
                and self.difficulty == EP.HARD:
            self.device.multiClick(self.assets.hard, 2)

            self.unlocked = [self.assets.part1_hard_unlocked]
            if self.assets.part1_hard_unlocked_2:
                self.unlocked.append(self.assets.part1_hard_unlocked_2)
            if self.assets.part1_hard_unlocked_3:
                self.unlocked.append(self.assets.part1_hard_unlocked_3)

            self.finished = [self.assets.part1_hard_finished]
            if self.assets.part1_hard_finished_2:
                self.finished.append(self.assets.part1_hard_finished_2)
            if self.assets.part1_hard_finished_3:
                self.finished.append(self.assets.part1_hard_finished_3)

            self.area_1 = self.assets.part1_hard_area_1
            self.area_2 = self.assets.part1_hard_area_2

        # 大活动 Part2 普通
        if self.type == EP.LARGE \
                and self.part == EP.PART_2 \
                and self.difficulty == EP.NORMAL:
            self.device.multiClick(self.assets.normal, 2)
            self.unlocked = [self.assets.part2_normal_unlocked]

            if self.assets.part2_normal_unlocked_2:
                self.unlocked.append(self.assets.part2_normal_unlocked_2)
            if self.assets.part2_normal_unlocked_3:
                self.unlocked.append(self.assets.part2_normal_unlocked_3)

            self.finished = [self.assets.part2_normal_finished]

            if self.assets.part2_normal_finished_2:
                self.finished.append(self.assets.part2_normal_finished_2)
            if self.assets.part2_normal_finished_3:
                self.finished.append(self.assets.part2_normal_finished_3)

            self.area_1 = self.assets.part2_normal_area_1
            self.area_2 = self.assets.part2_normal_area_2

        # 大活动 Part2 困难
        if self.type == EP.LARGE \
                and self.part == EP.PART_2 \
                and self.difficulty == EP.HARD:
            self.device.multiClick(self.assets.hard, 2)

            self.unlocked = [self.assets.part2_hard_unlocked]

            if self.assets.part2_hard_unlocked_2:
                self.unlocked.append(self.assets.part2_hard_unlocked_2)
            if self.assets.part2_hard_unlocked_3:
                self.unlocked.append(self.assets.part2_hard_unlocked_3)

            self.finished = [self.assets.part2_hard_finished]

            if self.assets.part2_hard_finished_2:
                self.finished.append(self.assets.part2_hard_finished_2)
            if self.assets.part2_hard_finished_3:
                self.finished.append(self.assets.part2_hard_finished_3)

            self.area_1 = self.assets.part2_hard_area_1
            self.area_2 = self.assets.part2_hard_area_2
        else:
            self.unlocked = [self.assets.part1_normal_unlocked]

            if self.assets.part1_normal_unlocked_2:
                self.unlocked.append(self.assets.part1_normal_unlocked_2)
            if self.assets.part1_normal_unlocked_3:
                self.unlocked.append(self.assets.part1_normal_unlocked_3)

            self.finished = [self.assets.part1_normal_finished]

            if self.assets.part1_normal_finished_2:
                self.finished.append(self.assets.part1_normal_finished_2)
            if self.assets.part1_normal_finished_3:
                self.finished.append(self.assets.part1_normal_finished_3)

            self.area_1 = self.assets.part1_normal_area_1
            self.area_2 = self.assets.part1_normal_area_2
        self.device.sleep(2)

    def checkRestChance(self):
        self.rest_chance = self.device.textStrategy(None, self.assets.rest_chance, OcrResult.TEXT)
        self.rest_chance = int(self.rest_chance.split('/')[0])
        if self.rest_chance > 0:
            self.INFO(f'rest chance: {self.rest_chance}')
            return True
        else:
            self.INFO('Event has no chance')

    def sroll_to_top(self):
        for i in range(2):
            self.device.swipe(360, 550, 360, 1000, 0.1)
            self.device.sleep(0.8)

    def sroll_to_bottom(self):
        for i in range(2):
            self.device.swipe(360, 1000, 360, 550, 0.1)
            self.device.sleep(0.8)

    @cached_property
    def assets(self):
        from module.task.event.event_assets import EventAssets
        from module.task.event.generateAssets import generateTemplate, generateAssets
        e = EventAssets()
        generateTemplate(f'./module/task/event/templates{self.path}')
        generateAssets(assets=e)
        return e

    @cached_property
    def pages(self):
        from module.ui.page import Page, page_main
        # 活动主页(大活动才有)
        event_page_main = Page(signs=[self.assets.event_page_main_sign], name='event_page_main', parent=page_main)
        event_page_main.link(button=home, destination=page_main)
        event_page_main.link(button=back, destination=page_main)

        # 活动—part1
        part1 = Page(signs=[self.assets.part1_sign], name='part1', parent=event_page_main)
        part1.link(button=home, destination=page_main)
        if self.type == EP.SMALL:
            part1.link(button=back, destination=page_main)
        elif self.type == EP.LARGE:
            part1.link(button=back, destination=event_page_main)

        event_page_main.link(button=self.assets.to_part1, destination=part1)

        # 活动—part1-关卡页
        part1_detail = Page(signs=[self.assets.step_sign], name='part1_detail', parent=event_page_main)
        part1_detail.link(button=home, destination=page_main)
        part1_detail.link(button=back, destination=part1)

        part1.link(button=self.assets.to_part1_detail, destination=part1_detail)

        # 活动—part2
        part2 = Page(signs=[self.assets.part2_sign], name='part2', parent=event_page_main)
        part2.link(button=home, destination=page_main)
        if self.type == EP.SMALL:
            part2.link(button=back, destination=page_main)
        elif self.type == EP.LARGE:
            part2.link(button=back, destination=event_page_main)

        event_page_main.link(button=self.assets.to_part2, destination=part2)

        # 活动—part2-关卡页
        part2_detail = Page(signs=[self.assets.step_sign], name='part2_detail', parent=event_page_main)
        part2_detail.link(button=home, destination=page_main)
        part2_detail.link(button=back, destination=part2)

        part2.link(button=self.assets.to_part2_detail, destination=part2_detail)

        # 如何是小活动，主页按钮链接到Part1
        if self.type == EP.SMALL:
            part1.parent = page_main
            page_main.link(button=self.assets.main_button, destination=part1)
            part1_detail.parent = part1
        # 如何是大活动，主页按钮链接到活动主页
        elif self.type == EP.LARGE:
            page_main.link(button=self.assets.main_button, destination=event_page_main)

        self.event_page_main = event_page_main
        self.part1 = part1
        self.part1_detail = part1_detail
        self.part2 = part2
        self.part2_detail = part2_detail

        return event_page_main

    def _go(self, destination):
        path1 = []
        self.getPathByBack(path1, UI.current_page)
        path2 = []
        self.getPathByParent(path2, destination)

        flag = False
        for i1, value1 in enumerate(path1):
            _destination1 = \
                list(filter(lambda x: x[1]['id'] == value1['button']['id'], path1[i1]['page'].links.items()))[0][0].name

            for i2, value2 in enumerate(path2):
                _destination2 = \
                    list(filter(lambda x: x[1]['id'] == value2['button']['id'], path2[i2]['page'].links.items()))[0][
                        0].name

                if _destination1 == _destination2:
                    path1 = path1[:i1 + 1]
                    path2 = path2[i2 + 1:]
                    flag = True
                    break

            if flag:
                break

        path = path1 + path2

        for index, value in enumerate(path):
            if value['destination'] is page_main:
                path = path[index + 1:]
                key = list(filter(lambda k: k is page_main, UI.current_page.links.keys()))
                if key:
                    path.insert(0, self.getPath(value['page'], page_main, UI.current_page.links[key[0]]))

            if value['page'] is UI.current_page and value['destination'] is destination:
                path = path[index:]

        for i in path:
            print(i)

        timeout = Timer(30).start()
        confirm_timer = Timer(limit=0, count=len(path)).start()
        click_timer = Timer(1.2)

        while 1:
            for index, value in enumerate(path):
                self.device.screenshot()

                if click_timer.reached() and self.device.appear_then_click(self.assets.touch_to_continue):
                    timeout.reset()
                    click_timer.reset()

                if click_timer.reached() and self.device.appear_then_click(self.assets.option):
                    timeout.reset()
                    click_timer.reset()

                if click_timer.reached() and self.device.clickTextLocation(text='SKIP', asset=self.assets.skip_area):
                    timeout.reset()
                    click_timer.reset()

                if self.device.appear(value['destination'].signs[0]):
                    path = path[index + 1:]
                    confirm_timer.count = len(path)
                    if confirm_timer.reached():
                        UI.current_page = destination
                        return

                    break

                if click_timer.reached() and self.device.appear_then_click(value['button']):
                    click_timer.reset()
                    timeout.reset()
                    click_timer.wait()
                    confirm_timer.reset()
                    click_timer.reset()

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
