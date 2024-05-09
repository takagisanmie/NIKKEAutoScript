import re
from functools import cached_property

from module.base.decorator import del_cached_property
from module.base.timer import Timer
from module.base.utils import exec_file, _area_offset, mask_area
from module.handler.assets import CONFIRM_B
from module.logger import logger
from module.map.map_grids import SelectedGrids
from module.shop.assets import *
from module.ui.assets import SHOP_CHECK
from module.ui.page import page_shop
from module.ui.ui import UI


class NotEnoughMoneyError(Exception):
    pass


class Refresh(Exception):
    pass


class ProductQueueIsEmpty(Exception):
    pass


class Product:
    def __init__(self, name, count, button):
        self.name = name
        self.timer = Timer(0, count=count - 1).start()
        self.button: Button = button

    def __str__(self):
        return f"Product: ({self.name}, count: {self.timer.count + 1})"


class ShopBase(UI):
    def ensure_into_shop(self, button, check, skip_first_screenshot=True):
        logger.hr(f"{check.name.split('_')[:1][0]} SHOP", 2)
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear(check, offset=(5, 5)):
                self.device.sleep(2)
                break

            if click_timer.reached() and self.appear_then_click(
                    button, offset=(5, 5), interval=5
            ):
                click_timer.reset()
                continue

    def p(self, button=None):
        click_timer = Timer(1.227)
        while 1:
            self.device.screenshot()

            if button is not None \
                    and click_timer.reached() \
                    and self.appear_then_click(button, offset=5, threshold=0.9, static=False) \
                    and button.match_appear_on(self.device.image, 10):
                click_timer.reset()
                continue

            if self.appear(
                    NO_MONEY, offset=(5, 5), static=False
            ) and NO_MONEY.match_appear_on(self.device.image):
                raise NotEnoughMoneyError

            if (
                    click_timer.reached()
                    and self.appear(MAX, offset=(30, 30), interval=3, static=False)
                    and MAX.match_appear_on(self.device.image, threshold=10)
            ):
                self.device.click(MAX)
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(
                    BUY, offset=(30, 30), interval=3, static=False
            ):
                click_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(1):
                skip_first_screenshot = True
                while 1:
                    if skip_first_screenshot:
                        skip_first_screenshot = False
                    else:
                        self.device.screenshot()
                    self.handle_reward(1)
                    if self.appear(SHOP_CHECK, offset=(5, 5)):
                        break

                # products = products.delete([products.first_or_none()])
                # logger.attr(
                #     "PENDING PRODUCT LIST", [i.name for i in products]
                # )
                # if products.first_or_none() is None:
                #     if refresh and not self.refreshed:
                #         raise Refresh
                #     break
                # product = products.first_or_none().button

                click_timer.reset()
                break

    def purchase(
            self,
            products: SelectedGrids,
            check_price=False,
            refresh=False,
            skip_first_screenshot=True,
    ):
        timeout = Timer(1.5, 2).start()
        click_timer = Timer(1.227)
        product: Button = products.first_or_none().button
        logger.attr("PENDING PRODUCT LIST", [i.name for i in products])

        while 1:
            try:
                if timeout.reached():
                    timeout.reset()
                    products = products.delete([products.first_or_none()])
                    logger.attr("PENDING PRODUCT LIST", [i.name for i in products])
                    if products.first_or_none() is None:
                        if refresh and not self.refreshed:
                            raise Refresh
                        break
                    product = products.first_or_none().button

                if skip_first_screenshot:
                    skip_first_screenshot = False
                else:
                    self.device.screenshot()

                if self.appear(PURCHASE_CHECK, offset=(5, 5), static=False):
                    self.p()

                else:
                    if self.appear(
                            product, offset=(5, 5), threshold=0.9, static=False
                    ) and product.match_appear_on(self.device.image, 10):
                        if check_price and product.name != ORNAMENT.name:
                            area = _area_offset(product.button, (-50, 0, 50, 250))
                            img = self.device.image[
                                  area[1]: area[3], area[0]: area[2]
                                  ]
                            super().__setattr__("_image", img)
                            if not self.credit_or_gratis:
                                skip_first_screenshot = True
                                self.device.image = mask_area(
                                    self.device.image, product.button
                                )
                                continue
                        if click_timer.reached():
                            self.device.click(product)
                            click_timer.reset()
                            timeout.reset()
                            continue

            except Refresh:
                if not self.refreshed:
                    confirm_timer = Timer(2, count=3).start()
                    click_timer = Timer(1.227)
                    while 1:
                        if skip_first_screenshot:
                            skip_first_screenshot = False
                        else:
                            self.device.screenshot()

                        if (
                                not self.refreshed
                                and click_timer.reached()
                                and self.appear(REFRESH, offset=(5, 5), static=False)
                        ):
                            x, y = REFRESH.location
                            self.device.click_minitouch(x - 80, y)
                            click_timer.reset()
                            confirm_timer.reset()

                        if (
                                click_timer.reached()
                                and self.appear(
                            GRATIS_REFRESH,
                            offset=(5, 5),
                            threshold=0.96,
                            static=False,
                        )
                                and self.appear_then_click(
                            CONFIRM_B, offset=(5, 5), static=False
                        )
                        ):
                            while 1:
                                self.device.screenshot()
                                self.appear_then_click(
                                    CONFIRM_B, offset=(5, 5), static=False
                                )
                                if SHOP_CHECK.appear_on(self.device.image):
                                    break

                            del self.__dict__["general_shop_priority"]
                            products = self.general_shop_priority
                            product: Button = products.first_or_none().button
                            self.refreshed = True
                            timeout.reset()
                            break

                        if click_timer.reached() and self.appear_then_click(
                                CANCEL, offset=(5, 5), interval=2, static=False
                        ):
                            click_timer.reset()
                            while 1:
                                self.device.screenshot()
                                if click_timer.reached() and self.appear_then_click(
                                        CANCEL, offset=(5, 5), static=False
                                ):
                                    click_timer.reset()
                                if SHOP_CHECK.appear_on(self.device.image):
                                    break
                            self.refreshed = True
                            timeout.reset()
                            break

    def purchase1(
            self,
            products: SelectedGrids,
            skip_first_screenshot=True,
    ):
        swipe_confirm = Timer(2, count=9).start()
        click_timer = Timer(0.6)
        product: Button = products.first_or_none().button
        logger.attr("PENDING PRODUCT LIST", [i.name for i in products])
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            for i in products:
                if self.appear(i.button, offset=5, threshold=0.9, static=False) \
                        and product.match_appear_on(self.device.image, 10):
                    if click_timer.reached():
                        self.device.click(i.button)
                        self.p(i.button)
                        if i.timer.reached():
                            products = products.delete([i])
                            logger.attr("PENDING PRODUCT LIST", [i.name for i in products])
                            if not products.count:
                                raise NotEnoughMoneyError
                            break
            if swipe_confirm.reached():
                raise NotEnoughMoneyError

            self.device.swipe((360, 1000), (360, 965), handle_control_check=False)
            self.device.sleep(1)
            # if (swipe_confirm.reached() and click_timer.reached()) or flag:
            #     products = products.delete([products.first_or_none()])
            #     logger.attr("PENDING PRODUCT LIST", [i.name for i in products])
            #     if products.first_or_none() is None:
            #         break
            #     product = products.first_or_none().button
            #     swipe_confirm.reset()
            #     flag = False
            # if skip_first_screenshot:
            #     skip_first_screenshot = False
            # else:
            #     self.device.screenshot()
            #
            # if self.appear(PURCHASE_CHECK, offset=(5, 5), static=False):
            #     self.p()
            #     if products.first_or_none().timer.reached():
            #         flag = True
            #         continue
            #     swipe_confirm.reset()
            # else:
            #     if self.appear(
            #         product, offset=(5, 5), threshold=0.9, static=False
            #     ) and product.match_appear_on(self.device.image, 10):
            #         if click_timer.reached():
            #             self.device.click(product)
            #             click_timer.reset()
            #     else:
            #         if (
            #             not swipe_confirm.reached(increase=False)
            #             and click_timer.reached()
            #         ):
            #             self.device.swipe(
            #                 (360, 1000), (360, 945), handle_control_check=False
            #             )
            #             self.device.sleep(1.6)
            #             swipe_confirm.reached()

    def ensure_back(self, check: Button, skip_first_screenshot=True):
        confirm_timer = Timer(1, count=1).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(
                    CANCEL, offset=(30, 30), interval=1, static=False
            ):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if (
                    self.appear(check, offset=(10, 10), static=False)
                    and confirm_timer.reached()
            ):
                break


class Shop(ShopBase):
    @cached_property
    def assets(self) -> dict:
        return exec_file("./module/shop/assets.py")

    @cached_property
    def general_shop_priority(self) -> SelectedGrids:
        priority = re.sub(r"\s+", "", self.config.GENERAL_SHOP_PRIORITY).split(">")
        return SelectedGrids(
            [
                Product(i, self.config.GENERAL_SHOP_PRODUCT.get(i), self.assets.get(i))
                for i in priority
            ]
        )

    @cached_property
    def arena_shop_priority(self) -> SelectedGrids:
        priority = re.sub(r"\s+", "", self.config.ArenaShop_priority).split(">")
        return SelectedGrids(
            [
                Product(i, self.config.ARENA_SHOP_PRODUCT.get(i), self.assets.get(i))
                for i in priority
            ]
        )

    @property
    def credit_or_gratis(self) -> bool:
        if GRATIS_B.match(
                self._image, offset=(5, 5), threshold=0.96, static=False
        ) and GRATIS_B.match_appear_on(self._image, threshold=5):
            return True
        elif CREDIT.match(
                self._image, offset=(5, 5), threshold=0.96, static=False
        ) and CREDIT.match_appear_on(self._image, threshold=5):
            return True

    def run(self):
        self.ui_ensure(page_shop)
        if self.config.GeneralShop_enable:
            super().__setattr__("refreshed", False)
            self.ensure_into_shop(GOTO_GENERAL_SHOP, GENERAL_SHOP_CHECK)
            self.purchase(self.general_shop_priority, True, True)
        try:
            if self.config.ArenaShop_enable:
                self.ensure_into_shop(GOTO_ARENA_SHOP, ARENA_SHOP_CHECK)
                if self.config.ArenaShop_priority is None or not len(
                        self.config.ArenaShop_priority.strip(" ")
                ):
                    raise ProductQueueIsEmpty
                self.purchase(self.arena_shop_priority)
        except NotEnoughMoneyError:
            logger.error("The rest of money is not enough to buy this product")
            self.ensure_back(ARENA_SHOP_CHECK)
        except ProductQueueIsEmpty:
            logger.warning("There are no products included in the queue option")
        del_cached_property(self, "general_shop_priority")
        del_cached_property(self, "arena_shop_priority")
        self.config.task_delay(server_update=True)
