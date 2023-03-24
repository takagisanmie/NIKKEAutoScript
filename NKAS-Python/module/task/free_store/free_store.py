import re
from common.enum.enum import ImgResult
from common.exception import Timeout
from module.base.task import Task
from module.task.free_store.free_store_assets import *
from module.task.free_store.free_store_assets import _1h, _2h
from module.task.free_store.free_store_assets import _cc, _cdc, _bdsc
from module.task.free_store.free_store_assets import _gem, _100K_credits
from module.task.free_store.free_store_assets import _1h_cdc, _1h_cc, _1h_bdsc
from module.task.free_store.free_store_assets import _2h_cdc, _2h_cc, _2h_bdsc
from module.task.free_store.free_store_assets import _Abnormal, _Tetra, _Pilgrim, _Missilis, _Elysion, _general_ticket

from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI


class FreeStore(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activate_rubbish_store = self.config.get('Task.FreeStore.activate_rubbish_store', self.config.task_dict)
        self.activate_arena_store = self.config.get('Task.FreeStore.activate_arena_store', self.config.task_dict)
        self.arena_product_list = self.config.get('Task.FreeStore.arena_product_list', self.config.task_dict)
        self.rubbish_store_product_list = self.config.get('Task.FreeStore.rubbish_store_product_list',
                                                          self.config.task_dict)

    def run(self):
        self.LINE('Free Store')
        self.into_general_store()
        if self.activate_arena_store:
            self.into_arena_store()
        if self.activate_rubbish_store:
            self.into_rubbish_store()
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

            if _refresh and click_timer.reached() and \
                    (self.device.appear_then_click(refresh) or self.device.appear_then_click(refresh_2)):
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
        if not self.rubbish_store_product_list:
            return

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

            if self.device.appear(product_sign):
                # 货币不足
                if self.device.appear(inadequate, img_template=cost_area, once=True):
                    # TODO 日志
                    selected_list.clear()
                    self.device.appear_then_click(close_product)
                    continue

                if click_timer.reached() and self.device.appear_then_click(confirm):
                    self.device.sleep(1.2)

                    timeout.reset()
                    confirm_timer.reset()
                    click_timer.reset()

                    selected_list = selected_list[1:]
                    continue

            else:
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

    def into_rubbish_store(self):
        if not self.rubbish_store_product_list:
            return

        pl = re.sub(r'\s+', '', self.rubbish_store_product_list)
        pl = pl.split('>')

        selected_list = []

        product_list = [_gem, _1h_cdc, _1h_cc, _1h_bdsc,
                        _2h_cdc, _2h_cc, _2h_bdsc, _100K_credits,
                        _general_ticket, _Elysion, _Missilis, _Tetra, _Pilgrim, _Abnormal
                        ]

        while 1:
            button = list(filter(lambda x: x['id'][1:] == pl[0], product_list))[0]
            selected_list.append(button)
            pl = pl[1:]
            if not pl:
                break

        if not selected_list:
            return

        timeout = Timer(90).start()
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()
            # 点击废铁商店
            if click_timer.reached() and self.device.appear_then_click(rubbish_store):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(close_product):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if selected_list:
                selected_list = self.buy_product_in_rubbish_store(selected_list)
                timeout.reset()

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def buy_product_in_rubbish_store(self, pl):
        self.device.sleep(0.3)
        timeout = Timer(60).start()
        confirm_timer = Timer(1, count=3).start()
        confirm_timer_2 = Timer(1, count=3).start()
        click_timer = Timer(1.2)

        # 当前最优先商品
        p = pl[0]

        exception = 'h'
        cases = [_1h_cdc, _1h_cc, _1h_bdsc, _2h_cdc, _2h_cc, _2h_bdsc]
        bought = False

        for i in range(2):
            self.device.swipe(360, 700, 360, 1100, 0.2)
            self.device.sleep(0.8)

        while 1:
            self.device.screenshot()

            # 获得界面
            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                confirm_timer.reset()
                confirm_timer_2.reset()
                click_timer.reset()
                self.device.sleep(1.2)
                continue

            # 在商品购买界面
            if self.device.appear(product_sign):

                # 货币不足
                if self.device.appear(inadequate, img_template=cost_area, once=True):
                    # TODO 日志
                    pl.clear()
                    return pl

                # 最大数量
                if self.device.appear_then_click(max_count, once=True):
                    self.device.sleep(0.3)

                # 购买
                if click_timer.reached() and self.device.appear_then_click(confirm):
                    bought = True
                    timeout.reset()
                    confirm_timer.reset()
                    confirm_timer_2.reset()
                    click_timer.reset()

                    # self.device.appear_then_click(close_product)
                    self.device.sleep(2)
                    continue

            else:
                if bought:
                    pl = pl[1:]
                    if pl:
                        return self.buy_product_in_rubbish_store(pl)
                    else:
                        return pl

                # 排除小时箱子  点击商品
                if exception not in p['id'] and click_timer.reached() and self.device.appear_then_click(p):
                    timeout.reset()
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                # 购买的商品是箱子
                elif p in cases:
                    if click_timer.reached():

                        type = None
                        if 'cc' in p['id']:
                            type = _cc
                        elif 'cdc' in p['id']:
                            type = _cdc
                        elif 'bdsc' in p['id']:
                            type = _bdsc

                        res = self.find_case(type, _1h if '1h' in p['id'] else _2h)

                        if res:
                            if click_timer.reached() and self.device.multiClickLocation(res[0], count=1):
                                timeout.reset()
                                confirm_timer.reset()
                                confirm_timer_2.reset()
                                click_timer.reset()
                                continue

            if confirm_timer.reached():
                if pl:
                    self.device.swipe(360, 1000, 360, 680, 0.3)
                    self.device.sleep(1.4)

                confirm_timer.reset()

                # 没找到商品
                if confirm_timer_2.reached():
                    pl = pl[1:]
                    if pl:
                        return self.buy_product_in_rubbish_store(pl)
                    else:
                        return pl

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def find_case(self, type, time):
        res = self.device.appear(type, _result=ImgResult.ALL_RESULT)
        if res:
            res = res[:1]
            lc = []
            for i in res:
                sl = self.device.matchRelative([i['left'], i['top'], i['right'], i['bottom']], left=0, right=30,
                                               top=100,
                                               bottom=120, template=time)
                if sl:
                    lc.append(i['location'])

            return lc
