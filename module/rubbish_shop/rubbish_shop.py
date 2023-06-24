import re
from datetime import datetime, timedelta, timezone
from functools import cached_property

from module.base.utils import exec_file
from module.logger import logger
from module.map.map_grids import SelectedGrids
from module.rubbish_shop.assets import *
from module.shop.shop import ShopBase, Product, NotEnoughMoneyError
from module.ui.page import page_shop


class RubbishShop(ShopBase):
    rubbish_shop_visited = set()

    @cached_property
    def assets(self) -> dict:
        return exec_file('./module/rubbish_shop/assets.py')

    @cached_property
    def rubbish_shop_priority(self) -> SelectedGrids:
        if self.config.RubbishShop_priority is None or not len(self.config.RubbishShop_priority.strip(' ')):
            priority = self.config.RUBBISH_SHOP_PRIORITY
        else:
            priority = self.config.RubbishShop_priority
        priority = re.sub(r'\s+', '', priority).split('>')
        return SelectedGrids(
            [Product(i, self.config.RUBBISH_SHOP_PRODUCT.get(i), self.assets.get(i)) for i in priority])

    @cached_property
    def next_tuesday(self) -> datetime:
        local_now = datetime.now()
        remain = (1 - local_now.weekday()) % 7
        remain = remain + 7 if remain == 0 else remain
        diff = datetime.now(timezone.utc).astimezone().utcoffset() - timedelta(hours=8)
        return local_now.replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(days=remain) + diff

    def run(self):
        self.ui_ensure(page_shop)
        self.ensure_into_shop(GOTO_RUBBISH_SHOP, RUBBISH_SHOP_CHECK)
        try:
            self._run(self.rubbish_shop_visited, self.rubbish_shop_priority, RUBBISH_SHOP_CHECK, swipe=True)
        except NotEnoughMoneyError:
            logger.error('The rest of money is not enough to buy this product')
            self.ensure_back(RUBBISH_SHOP_CHECK)
        self.rubbish_shop_visited.clear()
        self.config.task_delay(target=self.next_tuesday)
