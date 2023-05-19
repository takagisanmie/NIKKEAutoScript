import re
from functools import cached_property

from module.base.timer import Timer
from module.base.utils import exec_file, point2str
from module.handler.assets import CONFRIM_B
from module.logger import logger
from module.map.map_grids import SelectedGrids
from module.shop.assets import *
from module.ui.page import page_shop
from module.ui.ui import UI


class NotEnoughMoneyError(Exception):
    pass


class ProductQueueIsEmpty(Exception):
    pass


class Product:
    def __init__(self, name, count, button):
        self.name = name
        self.timer = Timer(0, count=count - 1)
        self.button: Button = button

    def __str__(self):
        return f'Product: ({self.name}, count: {self.timer.count + 1})'


class ShopBase(UI):
    def ensure_into_shop(self, button, check, skip_first_screenshot=True):
        logger.hr(f"{check.name.split('_')[:1][0]} SHOP", 2)
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(button, offset=(5, 5), interval=5):
                click_timer.reset()
                continue

            if self.appear(check, offset=(5, 5)):
                break

    def process(self, product: Product, visited: set, check: Button, swipe=False):
        logger.hr(product, 3)
        self.detect_product(product, check, swipe)
        if not product.timer.reached(increase=False):
            self.process(product, visited, check, swipe)
        else:
            self.device.stuck_record_clear()
            self.device.click_record_clear()
            visited.add(product.name)

    def detect_product(self, product: Product, check: Button, swipe=False):
        if swipe:
            self.ensure_sroll_to_top(x1=(360, 720), x2=(360, 920), delay=1.4)

        product.timer.start()
        confirm_timer = Timer(2, count=2).start()
        scroll_timer = Timer(0, count=4).start()
        click_timer = Timer(0.3)
        flag = False
        while 1:
            self.device.screenshot()

            if not flag \
                    and click_timer.reached() \
                    and self.appear(product.button, offset=(10, 10), static=False) \
                    and product.button.match_appear_on(self.device.image):
                self.device.click_minitouch(*product.button.location)
                logger.info(
                    'Click %s @ %s' % (point2str(*product.button.location), product.name)
                )
                self.device.sleep(1.2)
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.appear(NO_MONEY, offset=(5, 5), static=False) and NO_MONEY.match_appear_on(self.device.image):
                raise NotEnoughMoneyError

            if click_timer.reached() \
                    and self.appear(MAX, offset=(30, 30), interval=3) \
                    and MAX.match_appear_on(self.device.image, threshold=10):
                self.device.click(MAX)
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(BUY, offset=(30, 30), interval=3):
                flag = True
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(1):
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.appear(check, offset=(5, 5), static=False) and flag:
                product.timer.reached()
                break

            if self.appear(check, offset=(5, 5), static=False) and confirm_timer.reached():
                logger.warning('Perhaps all the products of the same type have been bought')
                product.timer.limit = 0
                product.timer.count = 0
                product.timer._reach_count = 1
                break

            if swipe:
                if not scroll_timer.reached(increase=False) \
                        and self.appear(check, offset=(5, 5), static=False) \
                        and click_timer.reached():
                    self.device.swipe((360, 1000), (360, 970), handle_control_check=False)
                    self.device.sleep(1.6)
                    scroll_timer.reached()
                    confirm_timer.reset()

    def _run(self, visited, priority, check, then=None, swipe=False):
        while len(visited) != len(priority):
            product_list = priority.delete(priority._select('name', visited).grids)
            logger.attr('PENDING PRODUCT LIST', [i.name for i in product_list])
            self.process(product_list.first_or_none(), visited, check, swipe)
            if callable(then):
                then(visited)

    def ensure_back(self, check: Button, skip_first_screenshot=True):
        confirm_timer = Timer(1, count=1).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(CANCEL, offset=(30, 30), interval=3):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(check, offset=(10, 10)) and confirm_timer.reached():
                break


class Shop(ShopBase):
    general_shop_visited = set()
    arena_shop_visited = set()

    @cached_property
    def assets(self) -> dict:
        return exec_file('./module/shop/assets.py')

    @cached_property
    def general_shop_priority(self) -> SelectedGrids:
        priority = re.sub(r'\s+', '', self.config.GENERAL_SHOP_PRIORITY).split('>')
        return SelectedGrids(
            [Product(i, self.config.GENERAL_SHOP_PRODUCT.get(i), self.assets.get(i)) for i in priority])

    @cached_property
    def arena_shop_priority(self) -> SelectedGrids:
        priority = re.sub(r'\s+', '', self.config.ArenaShop_priority).split('>')
        return SelectedGrids([Product(i, self.config.ARENA_SHOP_PRODUCT.get(i), self.assets.get(i)) for i in priority])

    def general_shop_after(self, visited: set, skip_first_screenshot=True):
        confirm_timer = Timer(2, count=3).start()
        click_timer = Timer(0.6)
        flag = False
        already_checked = False
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if not already_checked and click_timer.reached() and self.appear_then_click(REFRESH, offset=(5, 5),
                                                                                        interval=3, static=False):
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() \
                    and self.appear(GRATIS_REFRESH, offset=(5, 5), threshold=0.96, static=False) \
                    and self.appear_then_click(CONFRIM_B, offset=(5, 5), static=False):
                flag = True
                already_checked = True
                click_timer.reset()
                confirm_timer.reset()
                continue

            elif click_timer.reached() and self.appear(CONFRIM_B, offset=(5, 5), static=False):
                already_checked = True

            if not flag and already_checked and click_timer.reached() and self.appear_then_click(CANCEL, offset=(5, 5),
                                                                                                 interval=3,
                                                                                                 static=False):
                click_timer.reset()
                confirm_timer.reset()
                continue

            if already_checked and self.appear(GENERAL_SHOP_CHECK, offset=(5, 5)) and confirm_timer.reached():
                break

        if flag:
            visited.clear()

    def run(self):
        self.ui_ensure(page_shop)
        if self.config.GeneralShop_enable:
            self.ensure_into_shop(GOTO_GENERAL_SHOP, GENERAL_SHOP_CHECK)
            self._run(self.general_shop_visited, self.general_shop_priority, GENERAL_SHOP_CHECK,
                      then=self.general_shop_after)
        try:
            if self.config.ArenaShop_enable:
                self.ensure_into_shop(GOTO_ARENA_SHOP, ARENA_SHOP_CHECK)
                if self.config.ArenaShop_priority is None or not len(self.config.ArenaShop_priority.strip(' ')):
                    raise ProductQueueIsEmpty
                self._run(self.arena_shop_visited, self.arena_shop_priority, ARENA_SHOP_CHECK)
        except NotEnoughMoneyError:
            logger.error('The rest of money is not enough to buy this product')
            self.ensure_back(ARENA_SHOP_CHECK)
        except ProductQueueIsEmpty:
            logger.warning("There are no products included in the queue option")
        self.config.task_delay(server_update=True)
