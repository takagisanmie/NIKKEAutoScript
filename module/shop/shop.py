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
        self.timer = Timer(1, count=count - 1)
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


class Shop(ShopBase):
    # general shop
    def general_shop(self, skip_first_screenshot=True):
        confirm_timer = Timer(5, count=2).start()
        click_timer = Timer(1.8)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(GRATIS, offset=(5, 5), interval=5, static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(BUY, offset=(5, 5), interval=5, static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(interval=0.3):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(GENERAL_SHOP_CHECK, offset=(5, 5)) and confirm_timer.reached():
                break

    def ensure_fresh(self, skip_first_screenshot=True):
        confirm_timer = Timer(5, count=2).start()
        click_timer = Timer(1.8)
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
                continue

            if click_timer.reached() \
                    and self.appear(GRATIS_REFRESH, offset=(5, 5), threshold=0.96, static=False) \
                    and self.appear_then_click(CONFRIM_B, offset=(5, 5), static=False):
                flag = True
                already_checked = True
                click_timer.reset()
                continue

            elif click_timer.reached() and self.appear(CONFRIM_B, offset=(5, 5), static=False):
                already_checked = True

            if not flag and already_checked and click_timer.reached() and self.appear_then_click(CANCEL, offset=(5, 5),
                                                                                                 interval=3,
                                                                                                 static=False):
                click_timer.reset()
                continue

            if already_checked and confirm_timer.reached() and self.appear(GENERAL_SHOP_CHECK, offset=(5, 5)):
                break

        return flag

    # arena shop
    file = './module/shop/assets.py'
    visited = set()

    @cached_property
    def priority(self) -> SelectedGrids:
        if not self.config.ArenaShop_priority:
            priority = self.config.ARENA_SHOP_PRIORITY
        else:
            priority = self.config.ArenaShop_priority
        priority = re.sub(r'\s+', '', priority).split('>')
        result = exec_file(self.file)
        return SelectedGrids([Product(i, self.config.ARENA_SHOP_PRODUCT.get(i), result.get(i)) for i in priority])

    def _run(self):
        while len(self.visited) != len(self.priority):
            product_list = self.priority.delete(self.priority._select('name', self.visited).grids)
            logger.attr('PENDING PRODUCT LIST', [i.name for i in product_list])
            self.process(product_list.first_or_none())

    def process(self, product: Product):
        logger.hr(product, 3)
        self.detect_product(product)
        if not product.timer.reached(increase=False):
            self.process(product)
        else:
            self.visited.add(product.name)

    def detect_product(self, product: Product):
        product.timer.start()
        confirm_timer = Timer(2, count=2).start()
        click_timer = Timer(0.3)
        flag = False
        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.appear(product.button, offset=(10, 10), static=False) \
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

            if click_timer.reached() and self.appear_then_click(MAX, offset=(30, 30), interval=3):
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

            if self.appear(ARENA_SHOP_CHECK, offset=(5, 5), static=False) and flag:
                product.timer.reached()
                break

            if self.appear(ARENA_SHOP_CHECK, offset=(5, 5), static=False) and click_timer.reached():
                logger.warning('Perhaps all the products of the same type have been bought')
                product.timer.limit = 0
                product.timer.count = 0
                product.timer._reach_count = 1
                break

    def ensure_back(self, skip_first_screenshot=True):
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

            if self.appear(ARENA_SHOP_CHECK, offset=(10, 10)) and confirm_timer.reached():
                break

    def run(self):
        self.ui_ensure(page_shop)
        if self.config.GeneralShop_enable:
            self.ensure_into_shop(GOTO_GENERAL_SHOP, GENERAL_SHOP_CHECK)
            self.general_shop()
            if self.ensure_fresh():
                self.general_shop()
        try:
            if self.config.ArenaShop_enable:
                self.ensure_into_shop(GOTO_ARENA_SHOP, ARENA_SHOP_CHECK)
                if not self.config.ArenaShop_priority:
                    raise ProductQueueIsEmpty
                self._run()
        except NotEnoughMoneyError:
            logger.error('The rest of money is not enough to buy this product')
            self.ensure_back()
        except ProductQueueIsEmpty:
            logger.warning("There are no products included in the queue option")
        self.config.task_delay(server_update=True)
