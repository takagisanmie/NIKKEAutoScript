import re
from datetime import datetime, timedelta, timezone
from functools import cached_property

from module.base.timer import Timer
from module.base.utils import exec_file, point2str
from module.logger import logger
from module.map.map_grids import SelectedGrids
from module.rubbish_shop.assets import *
from module.shop.shop import ShopBase
from module.ui.page import page_shop


class NotEnoughMoneyError(Exception):
    pass


class Product:
    def __init__(self, name, count, button):
        self.name = name
        self.timer = Timer(1, count=count - 1)
        self.button: Button = button

    def __str__(self):
        return f'Product: ({self.name}, count: {self.timer.count + 1})'


class RubbishShop(ShopBase):
    file = './module/rubbish_shop/assets.py'
    visited = set()

    @cached_property
    def priority(self) -> SelectedGrids:
        if not self.config.RubbishShop_priority:
            priority = self.config.RUBBISH_SHOP_PRIORITY
        else:
            priority = self.config.RubbishShop_priority
        priority = re.sub(r'\s+', '', priority).split('>')
        result = exec_file(self.file)
        return SelectedGrids([Product(i, self.config.RUBBISH_SHOP_PRODUCT.get(i), result.get(i)) for i in priority])

    @cached_property
    def next_tuesday(self) -> datetime:
        local_now = datetime.now()
        remain = (1 - local_now.weekday()) % 7
        diff = datetime.now(timezone.utc).astimezone().utcoffset() - timedelta(hours=8)
        return local_now.replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(days=remain) + diff

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
        self.ensure_sroll_to_top(x1=(360, 720), x2=(360, 920), delay=1.4)
        product.timer.start()
        confirm_timer = Timer(8, count=4).start()
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

            if confirm_timer.reached():
                logger.warning('Perhaps all the products of the same type have been bought')
                product.timer.count = 0
                product.timer._reach_count = 1
                break

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

            if self.appear(RUBBISH_SHOP_CHECK, offset=(5, 5), static=False) and flag:
                product.timer.reached()
                break

            if self.appear(RUBBISH_SHOP_CHECK, offset=(5, 5), static=False) and click_timer.reached():
                self.device.swipe((360, 1000), (360, 960), handle_control_check=False)
                self.device.sleep(1.4)

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

            if self.appear(RUBBISH_SHOP_CHECK, offset=(10, 10)) and confirm_timer.reached():
                break

    def run(self):
        self.ui_ensure(page_shop)
        self.ensure_into_shop(GOTO_RUBBISH_SHOP, RUBBISH_SHOP_CHECK)
        try:
            self._run()
        except NotEnoughMoneyError:
            logger.error('The rest of money is not enough to buy this product')
            self.ensure_back()
        self.config.task_delay(target=self.next_tuesday)
