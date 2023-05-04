from datetime import datetime, timedelta, timezone
from functools import cached_property

from module.rubbish_shop.assets import *
from module.shop.shop import ShopBase
from module.ui.page import page_shop


class RubbishShop(ShopBase):

    @cached_property
    def next_tuesday(self) -> datetime:
        local_now = datetime.now()
        remain = (1 - local_now.weekday()) % 7
        diff = datetime.now(timezone.utc).astimezone().utcoffset() - timedelta(hours=8)
        return local_now.replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(days=remain) + diff

    def run(self):
        self.ui_ensure(page_shop)
        self.ensure_into_shop(GOTO_RUBBISH_SHOP, RUBBISH_SHOP_CHECK)
        self.config.task_delay(target=self.next_tuesday)
