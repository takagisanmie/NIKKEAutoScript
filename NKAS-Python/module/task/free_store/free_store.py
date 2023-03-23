from common.enum.enum import ImgResult
from common.exception import Timeout
from module.base.task import Task
from module.task.free_store.free_store_assets import *
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI


class FreeStore(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activate_arena_store = self.config.get('Task.FreeStore.activate_arena_store', self.config.task_dict)
        self.arena_product_list = self.config.get('Task.FreeStore.arena_product_list', self.config.task_dict)

    def run(self):
        self.LINE('Free Store')
        self.into_general_store()
        if self.activate_arena_store:
            self.into_arena_store()
        self.finish(self.config, 'FreeStore')
        self.INFO('Free Store is finished')
        self.go(page_main)

    def into_general_store(self):
        self.go(destination=page_free_store)
        self.buy_free_product()

    def buy_free_product(self):
        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        _refresh = True

        while 1:
            self.device.screenshot()
            if click_timer.reached() and self.device.appear_then_click(general_store):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(free_sale):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear(free_sale_2) and self.device.appear_then_click(
                    confirm, value=0.75,
                    img_template=bottom):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if _refresh and click_timer.reached() and self.device.appear_then_click(refresh):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.appear(refresh_sign):
                _refresh = False

            if click_timer.reached() \
                    and self.device.appear(refresh_sign) \
                    and self.device.appear(free_refresh) \
                    and self.device.appear_then_click(confirm, value=0.75, img_template=middle):
                self.INFO('refresh store')
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(cancel_2):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def into_arena_store(self):
        import re
        pl = re.sub(r'\s+', '', self.arena_product_list)
        pl = pl.split('>')

        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(arena_store):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached():
                break

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

        product_list = [electric, fire, water, wind, iron, selection_box]
        selected_list = []

        while 1:
            button = list(filter(lambda x: x['id'] == pl[0], product_list))[0]
            selected_list.append(button)
            pl = pl[1:]
            if not pl:
                break

        if not selected_list:
            return

        res = self.device.appear(selected_list, _result=ImgResult.ALL_RESULT, sort_by=None)
        selected_list.clear()

        for i in res:
            left, right, top, bottom = i['left'], i['right'], i['top'], i['bottom']

            position = [left, top, right, bottom]

            sl = self.device.matchRelative(position, left=-80, right=70, top=20, bottom=60, template=sold_out)
            if not sl:
                selected_list.append(i['location'])

        if not selected_list:
            return

        timeout.reset()
        confirm_timer.reset()
        click_timer.reset()

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(confirm):
                self.device.sleep(1.2)

                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()

                selected_list = selected_list[1:]

                continue

            if selected_list and click_timer.reached() \
                    and self.device._hide(product_sign) \
                    and self.device.uiautomator_click(selected_list[0][0], selected_list[0][1]):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.device.appear(free_store_sign) and confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
