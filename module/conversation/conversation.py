from module.base.timer import Timer
from module.base.utils import (
    point2str,
    find_center,
)
from module.conversation.assets import (
    DETAIL_CHECK,
    GIFT,
    OPPORTUNITY,
    OPPORTUNITY_B,
    COMMUNICATE,
    FAVOURITE_CHECK,
    ANSWER_CHECK,
    RANK_INCREASE_COMFIRM,
    COMMUNICATE_QUICKLY,
)
from module.handler.assets import CONFIRM_B, AUTO_CLICK_CHECK
from module.logger import logger
from module.ui.assets import CONVERSATION_CHECK, GOTO_BACK
from module.ui.page import page_conversation
from module.ui.ui import UI


class ChooseNextNIKKETooLong(Exception):
    pass


class NoOpportunitiesRemain(Exception):
    pass


class ConversationQueueIsEmpty(Exception):
    pass


class Conversation(UI):
    _confirm_timer = Timer(4, count=10)

    @property
    def opportunity_remain(self):
        result = OPPORTUNITY.appear_on(self.device.image, threshold=25)
        logger.info(f"[Opportunity remain] {result}")
        return result

    def get_next_target(self):
        if DETAIL_CHECK.match(self.device.image, threshold=0.71) and GIFT.match_appear_on(self.device.image,
                                                                                          threshold=10):
            if OPPORTUNITY_B.match(self.device.image, offset=5, threshold=0.96, static=False):
                logger.warning("There are no remaining opportunities")
                raise NoOpportunitiesRemain

            if not COMMUNICATE.match_appear_on(self.device.image, 10):
                if self._confirm_timer.reached():
                    logger.warning("Perhaps all selected NIKKE already had a conversation")
                    raise ChooseNextNIKKETooLong
                self.device.click_minitouch(690, 560)
            else:
                self._confirm_timer.reset()
                self.device.stuck_record_clear()
                self.device.click_record_clear()
                return
        else:
            try:
                if CONVERSATION_CHECK.match(self.device.image, offset=5):
                    if not self.opportunity_remain:
                        logger.warning("There are no remaining opportunities")
                        raise NoOpportunitiesRemain
                    r = [
                        i.get("area")
                        for i in FAVOURITE_CHECK.match_several(
                            self.device.image, threshold=0.71, static=False
                        )
                    ]
                    r.sort(key=lambda x: x[1])
                    self.device.click_minitouch(*find_center(r[0]))
            except Exception:
                pass

        self.device.sleep(1.3)
        self.device.screenshot()
        self.get_next_target()

    def communicate(self):
        logger.hr("Start a conversation")
        self.get_next_target()
        self.ensure_wait_to_answer()

    def ensure_wait_to_answer(self, skip_first_screenshot=True):
        confirm_timer = Timer(1.6, count=2).start()
        click_timer = Timer(0.9)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() \
                    and COMMUNICATE_QUICKLY.match_appear_on(self.device.image, threshold=6) \
                    and self.appear_then_click(COMMUNICATE_QUICKLY, offset=5, interval=3):
                confirm_timer.reset()
                click_timer.reset()
                continue

            elif click_timer.reached() \
                    and COMMUNICATE.match_appear_on(self.device.image, threshold=6) \
                    and self.appear_then_click(COMMUNICATE, offset=5, interval=3):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(CONFIRM_B, offset=(5, 5), static=False):
                x, y = CONFIRM_B.location
                self.device.click_minitouch(x - 75, y)
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(ANSWER_CHECK, offset=1, threshold=0.9, static=False):
                self.answer()

            elif not COMMUNICATE.match_appear_on(self.device.image, threshold=6) \
                    and self.appear(DETAIL_CHECK, offset=(5, 5), static=False) \
                    and GIFT.match_appear_on(self.device.image, threshold=10) \
                    and confirm_timer.reached():
                return self.communicate()

            if self.appear(AUTO_CLICK_CHECK, offset=(30, 30), interval=0.3):
                self.device.click_minitouch(100, 100)
                logger.info("Click %s @ %s" % (point2str(100, 100), "WAIT_TO_ANSWER"))
                click_timer.reset()
                continue

            if click_timer.reached() and not GIFT.match_appear_on(self.device.image, threshold=10):
                self.device.click_minitouch(100, 100)
                click_timer.reset()
                continue

    def answer(self, skip_first_screenshot=True):
        click_timer = Timer(0.5)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear(DETAIL_CHECK, offset=(30, 30), static=False) and GIFT.match_appear_on(self.device.image,
                                                                                                 threshold=10):
                break

            if click_timer.reached():
                self.device.click_minitouch(*ANSWER_CHECK.location)
                logger.info(
                    "Click %s @ %s" % (point2str(*ANSWER_CHECK.location), "ANSWER")
                )
                click_timer.reset()
                continue

        self.device.sleep(2.5)
        # return self.communicate()
        # self.ensure_back()

    def ensure_back(self, skip_first_screenshot=True):
        confirm_timer = Timer(2, count=3).start()
        click_timer = Timer(0.3)

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(
                    RANK_INCREASE_COMFIRM, offset=(10, 10), interval=0.3, static=False
            ):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if (
                    click_timer.reached()
                    and not self.appear(CONVERSATION_CHECK, offset=(10, 10))
                    and self.appear_then_click(GOTO_BACK, offset=(10, 10), interval=3)
            ):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if (
                    self.appear(CONVERSATION_CHECK, offset=(10, 10))
                    and confirm_timer.reached()
            ):
                break

        return self.communicate()

    def ensure_opportunity_remain(self):
        if self.opportunity_remain:
            return True

    def run(self):
        self.ui_ensure(page_conversation, confirm_wait=1)
        for i in range(3):
            self.device.click_minitouch(412, 445)
            self.device.sleep(0.3)
        if self.ensure_opportunity_remain():
            self._confirm_timer.reset().start()
            try:
                self.communicate()
            except ChooseNextNIKKETooLong as e:
                logger.error(e)
            except NoOpportunitiesRemain as e:
                logger.error(e)
            except ConversationQueueIsEmpty as e:
                logger.error(e)
        else:
            logger.info("There are no opportunities remaining")
        self.config.task_delay(server_update=True)
