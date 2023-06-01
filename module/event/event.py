from datetime import timedelta, datetime, timezone
from functools import cached_property

from module.base.decorator import Config
from module.base.timer import Timer
from module.base.utils import point2str, crop, _area_offset
from module.event.assets import HARD_AVAILABLE_CHECK
from module.logger import logger
from module.map.map_grids import SelectedGrids
from module.simulation_room.assets import AUTO_SHOOT, AUTO_BURST, PAUSE
from module.ui.assets import GOTO_BACK
from module.ui.page import page_main, page_event, page_story_1, MAIN_GOTO_EVENT, EVENT_GOTO_STORY_1, page_story_2, \
    STORY_1_NORMAL_CHECK, \
    STORY_1_HARD_CHECK, STORY_2_NORMAL_CHECK, STORY_2_HARD_CHECK, STORY_1_GOTO_STAGE_LIST, STORY_2_GOTO_STAGE_LIST, \
    STAGE_CHECK, STORY_1_NORMAL_UNLOCKED, STORY_1_NORMAL_COMPLETED, STORY_1_NORMAL_LOCKED, STORY_2_NORMAL_UNLOCKED, \
    STORY_2_NORMAL_LOCKED, STORY_2_NORMAL_COMPLETED, STORY_1_HARD_LOCKED, STORY_1_HARD_COMPLETED, STORY_1_HARD_UNLOCKED, \
    STORY_2_HARD_LOCKED, STORY_2_HARD_UNLOCKED, STORY_2_HARD_COMPLETED, STORY_1_NORMAL_STAGE_AREA_A, \
    STORY_1_NORMAL_STAGE_AREA_B, STORY_1_HARD_STAGE_AREA_B, STORY_1_HARD_STAGE_AREA_A, STORY_2_HARD_STAGE_AREA_B, \
    STORY_2_NORMAL_STAGE_AREA_A, STORY_2_NORMAL_STAGE_AREA_B, STORY_2_HARD_STAGE_AREA_A, STAGE_DETAILED_CHECK, FIGHT, \
    NEXT_STAGE, END_CHECK, FIGHT_QUICKLY, MAX, QUICK_FIGHT_CONFIRM, STORY_1_NORMAL_NO_OPPORTUNITY, \
    STORY_1_HARD_NO_OPPORTUNITY, \
    STORY_2_NORMAL_NO_OPPORTUNITY, STORY_2_HARD_NO_OPPORTUNITY, QUICK_FIGHT_CHECK
from module.ui.ui import UI


class EventPartError(Exception):
    pass


class EventDifficultyError(Exception):
    pass


class EventPartUnavailableError(Exception):
    pass


class HardEventAvailable(Exception):
    pass


class EventUnavailableError(Exception):
    pass


class NoOpportunityRemain(Exception):
    pass


class EventInfo:
    def __init__(self, id, name, type, duration, update_date):
        self.id: str = id
        self.name: str = name
        self.type: int = type
        self.duration: timedelta = duration
        self.update_date: datetime = update_date


class Stage:
    def __init__(self, type: str, location: tuple):
        self.type = type
        self.location = location


class Event(UI):
    diff = datetime.now(timezone.utc).astimezone().utcoffset() - timedelta(hours=8)

    @cached_property
    def event(self) -> EventInfo:
        for k, v in self.config.EVENTS[0].items():
            self.config.__setattr__(k, v)
        return EventInfo(*self.config.EVENTS[0].values())

    @cached_property
    def event_story_2_is_available(self) -> bool:
        when = self.event.update_date + timedelta(days=7) + self.diff
        local_now = datetime.now()
        super().__setattr__('event_story_2', when)
        super().__setattr__('event_story_2_second_part', True if local_now > when + timedelta(days=7) else False)
        if local_now > when:
            return True

    @cached_property
    def event_story_second_part_is_available(self) -> bool:
        when = self.event.update_date + timedelta(days=7) + self.diff
        local_now = datetime.now()
        super().__setattr__('event_story_second_part', when)
        if local_now > when:
            return True

    @cached_property
    def event_story_1_difficulty_area(self):
        return [(460, 1200), (640, 1200)]

    @cached_property
    def event_story_2_difficulty_area(self):
        return [(450, 1200), (590, 1200)]

    @cached_property
    def stage(self) -> int:
        if not self.config.Event_Event_Name:
            self.config.Event_Event_Name = '1-11'
        logger.attr('STAGE NAME', self.config.Event_Event_Name)
        prefix, suffix = self.config.Event_Event_Name.strip(' ').split('-')
        return int(suffix)

    def stage_list(self, area):
        image = self.crop(area)

        available_stage = [Stage(type='available', location=_area_offset(i.get('location'), (area[0], area[1]))) for i
                           in
                           self.unlocked.match_several(image, offset=5, threshold=0.82, static=False)]
        completed_stage = [Stage(type='completed', location=_area_offset(i.get('location'), (area[0], area[1]))) for i
                           in
                           self.completed.match_several(image, offset=5, threshold=0.8, static=False)]
        locked_stage = [Stage(type='locked', location=_area_offset(i.get('location'), (area[0], area[1]))) for i in
                        self.locked.match_several(image, offset=5, threshold=0.8, static=False)]
        return SelectedGrids(available_stage + completed_stage + locked_stage)

    def ensure_event_button(self):
        if self.event.type == 1:
            if self.config.Event_Part == 'story_1':
                unlocked = STORY_1_NORMAL_UNLOCKED
                completed = STORY_1_NORMAL_COMPLETED
                locked = STORY_1_NORMAL_LOCKED
                area_a = STORY_1_NORMAL_STAGE_AREA_A
                area_b = STORY_1_NORMAL_STAGE_AREA_B
                no_opportunity = STORY_1_NORMAL_NO_OPPORTUNITY
            else:
                if self.config.Event_Difficulty == 'normal':
                    unlocked = STORY_2_NORMAL_UNLOCKED
                    completed = STORY_2_NORMAL_COMPLETED
                    locked = STORY_2_NORMAL_LOCKED
                    area_a = STORY_2_NORMAL_STAGE_AREA_A
                    area_b = STORY_2_NORMAL_STAGE_AREA_B
                    no_opportunity = STORY_2_NORMAL_NO_OPPORTUNITY
                else:
                    unlocked = STORY_2_HARD_UNLOCKED
                    completed = STORY_2_HARD_COMPLETED
                    locked = STORY_2_HARD_LOCKED
                    area_a = STORY_2_HARD_STAGE_AREA_A
                    area_b = STORY_2_HARD_STAGE_AREA_B
                    no_opportunity = STORY_2_HARD_NO_OPPORTUNITY
        else:
            if self.config.Event_Difficulty == 'normal':
                unlocked = STORY_1_NORMAL_UNLOCKED
                completed = STORY_1_NORMAL_COMPLETED
                locked = STORY_1_NORMAL_LOCKED
                area_a = STORY_1_NORMAL_STAGE_AREA_A
                area_b = STORY_1_NORMAL_STAGE_AREA_B
                no_opportunity = STORY_1_NORMAL_NO_OPPORTUNITY
            else:
                unlocked = STORY_1_HARD_UNLOCKED
                completed = STORY_1_HARD_COMPLETED
                locked = STORY_1_HARD_LOCKED
                area_a = STORY_1_HARD_STAGE_AREA_A
                area_b = STORY_1_HARD_STAGE_AREA_B
                no_opportunity = STORY_1_HARD_NO_OPPORTUNITY
        self.unlocked = unlocked
        self.completed = completed
        self.locked = locked
        self.area_a = area_a
        self.area_b = area_b
        self.no_opportunity = no_opportunity

    @Config.when(event_type=1)
    def redirect(self):
        page_main.link(button=MAIN_GOTO_EVENT, destination=page_event)
        page_event.link(button=EVENT_GOTO_STORY_1, destination=page_story_1)

    @Config.when(event_type=2)
    def redirect(self):
        page_main.link(button=MAIN_GOTO_EVENT, destination=page_story_1)

    def run(self):
        self.ui_ensure(page_main, confirm_wait=3)
        try:
            if not self.appear(MAIN_GOTO_EVENT, offset=(5, 5), static=False):
                raise EventUnavailableError
            _ = self.event
            self.redirect()
            self.ensure_into_event_page()
            self.ensure_into_stage_list()
            self.ensure_event_button()
            self.ensure_opportunity_remain()
            if self.config.Event_Complete_Event:
                self.detect_available_stage()
            self._loop()
        except EventPartError as e:
            logger.error(e)
        except EventDifficultyError as e:
            logger.error(e)
        except EventPartUnavailableError as e:
            logger.error(e)
        except HardEventAvailable as e:
            self.ensure_back()
            logger.error(e)
        except NoOpportunityRemain as e:
            self.ensure_back()
            logger.warning('There are no opportunities remaining')
        except EventUnavailableError as e:
            logger.error('The event is no longer available')
        self.config.task_delay(server_update=True)

    @Config.when(event_type=1)
    def ensure_into_event_page(self):
        logger.attr('PART', self.config.Event_Part)
        logger.attr('DIFFICULTY', self.config.Event_Difficulty)
        # large event
        if self.config.Event_Part == 'story_1':
            if self.config.Event_Difficulty != 'normal':
                raise EventDifficultyError('The current part is only available in normal level')
            if self.event_story_2_is_available:
                raise HardEventAvailable("'Story 2' is available currently")
        if self.config.Event_Part == 'story_2':
            if not self.event_story_2_is_available:
                raise EventPartUnavailableError(
                    f"'Story 2' is unavailable currently, it will be available on {self.event_story_2}")
            if self.config.Event_Difficulty == 'normal':
                if self.event_story_2_second_part:
                    raise HardEventAvailable('Higher difficulty levels are available.')
            if self.config.Event_Difficulty == 'hard':
                if not self.event_story_2_second_part:
                    raise EventPartUnavailableError(
                        f"'The second part of Story 2' is unavailable currently, it will be available on {self.event_story_2 + timedelta(days=7)}")
        if self.config.Event_Part == 'story_1':
            self.ui_ensure(page_story_1)
        elif self.config.Event_Part == 'story_2':
            self.ui_ensure(page_story_2)

    @Config.when(event_type=2)
    def ensure_into_event_page(self):
        logger.attr('PART', self.config.Event_Part)
        logger.attr('DIFFICULTY', self.config.Event_Difficulty)
        # small event
        if self.config.Event_Part != 'story_1':
            raise EventPartError('The current event only has a single part')
        if self.config.Event_Difficulty == 'normal':
            if self.event_story_second_part_is_available:
                raise HardEventAvailable('Higher difficulty levels are available.')
        if self.config.Event_Difficulty == 'hard':
            if not self.event_story_second_part_is_available:
                raise EventPartUnavailableError(
                    f"'The second part of Story 1' is unavailable currently, it will be available on {self.event_story_second_part}")
        self.ui_ensure(page_story_1)

    @Config.when(event_type=1)
    def ensure_into_stage_list(self, skip_first_screenshot=True):
        confirm_timer = Timer(2, count=3).start()
        click_timer = Timer(0.3)
        click_timer_2 = Timer(2)

        if self.config.Event_Part == 'story_1':
            check = STORY_1_NORMAL_CHECK
            button = STORY_1_GOTO_STAGE_LIST
            level_button = None
        else:
            if self.config.Event_Difficulty == 'normal':
                check = STORY_2_NORMAL_CHECK
                level_button = self.event_story_2_difficulty_area[0]
            else:
                check = STORY_2_HARD_CHECK
                level_button = self.event_story_2_difficulty_area[1]
            button = STORY_2_GOTO_STAGE_LIST

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(button, offset=(10, 10), interval=3,
                                                                static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer_2.reached() and isinstance(level_button, tuple) \
                    and not self.appear(check, offset=(10, 10), static=False) \
                    and not self.appear(button, offset=(10, 10), static=False):
                self.device.click_minitouch(*level_button)
                logger.info(
                    'Click %s @ %s' % (point2str(*level_button), 'LEVEL_BUTTON')
                )
                confirm_timer.reset()
                click_timer_2.reset()
                continue

            if self.appear(check, offset=(10, 10)) and confirm_timer.reached():
                break

    @Config.when(event_type=2)
    def ensure_into_stage_list(self, skip_first_screenshot=True):
        confirm_timer = Timer(2, count=3).start()
        click_timer = Timer(0.3)
        click_timer_2 = Timer(2)

        if self.config.Event_Difficulty == 'normal':
            check = STORY_1_NORMAL_CHECK
            level_button = self.event_story_1_difficulty_area[0]
        else:
            check = STORY_1_HARD_CHECK
            level_button = self.event_story_1_difficulty_area[1]
        button = STORY_1_GOTO_STAGE_LIST

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(button, offset=(10, 10), interval=3,
                                                                static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer_2.reached() and isinstance(level_button, tuple) \
                    and not self.appear(check, offset=(10, 10), static=False) \
                    and not self.appear(button, offset=(10, 10), static=False):
                self.device.click_minitouch(*level_button)
                logger.info(
                    'Click %s @ %s' % (point2str(*level_button), 'LEVEL_BUTTON')
                )
                confirm_timer.reset()
                click_timer_2.reset()
                continue

            if self.appear(check, offset=(10, 10)) and confirm_timer.reached():
                break

    def detect_available_stage(self):
        self.ensure_sroll_to_top(x1=(360, 460), x2=(360, 950))
        logger.hr('STAGE AREA A', 2)
        stage_list = self.stage_list(self.area_a.area)
        stage_list = stage_list.select(type='available')
        logger.attr('AVAILABLE STAGE COUNT', stage_list.count)
        if stage := stage_list.first_or_none():
            self.loop(stage, goto_next_stage=True)
        else:
            logger.info('All the stages in area A have been completed')
        self.ensure_sroll_to_bottom(x1=(360, 950), x2=(360, 460))
        logger.hr('STAGE AREA B', 2)
        stage_list = self.stage_list(self.area_b.area)
        stage_list = stage_list.select(type='available')
        logger.attr('AVAILABLE STAGE COUNT', stage_list.count)
        if stage := stage_list.first_or_none():
            self.loop(stage, goto_next_stage=True)
        else:
            logger.info('All the stages in area B have been completed')
            self.config.modified[f"Event.Event.Complete_Event"] = False

    def _loop(self):
        logger.hr('LOOP', 2)
        self.ensure_sroll_to_top(x1=(360, 460), x2=(360, 950))
        logger.hr('STAGE AREA A', 2)
        stage_a_list = self.stage_list(self.area_a.area)
        stage_a_list = stage_a_list.select(type='completed')
        logger.attr('COMPLETED STAGE COUNT', stage_a_list.count)
        stage_a_list.sort('location', 1)
        if stage_a_list.count >= self.stage:
            self.loop(stage_a_list.__getitem__(self.stage - 1))
        else:
            self.ensure_sroll_to_bottom(x1=(360, 950), x2=(360, 460))
            logger.hr('STAGE AREA B', 2)
            stage_b_list = self.stage_list(self.area_b.area)
            stage_b_list = stage_b_list.select(type='completed')
            logger.attr('COMPLETED STAGE COUNT', stage_b_list.count)
            stage_b_list.sort('location', 1)
            self.loop(stage_b_list.__getitem__(self.stage - 1 - stage_a_list.count))

    def loop(self, stage: Stage, skip_first_screenshot=True, goto_next_stage=False):
        confirm_timer = Timer(8, count=5).start()
        click_timer = Timer(0.3)
        click_timer_2 = Timer(3)
        if not goto_next_stage:
            while 1:
                if skip_first_screenshot:
                    skip_first_screenshot = False
                else:
                    self.device.screenshot()

                if click_timer_2.reached() \
                        and self.appear(STAGE_CHECK, offset=(5, 5), static=False) \
                        and not self.appear(STAGE_DETAILED_CHECK, offset=(5, 5), static=False) \
                        and not self.appear(QUICK_FIGHT_CHECK, offset=(5, 5), static=False):
                    self.device.click_minitouch(*stage.location)
                    logger.info('Click %s @ %s' % (point2str(*stage.location), 'STAGE'))
                    confirm_timer.reset()
                    click_timer_2.reset()
                    continue

                if click_timer.reached() and self.appear_then_click(FIGHT_QUICKLY, offset=(5, 5), interval=5,
                                                                    static=False):
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if click_timer.reached() and self.appear_then_click(MAX, offset=(5, 5), interval=1,
                                                                    static=False):
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if click_timer.reached() and self.appear_then_click(QUICK_FIGHT_CONFIRM, offset=(5, 5), interval=1,
                                                                    static=False):
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if click_timer.reached() and self.handle_event(1):
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if self.appear(END_CHECK, offset=(5, 5), static=False):
                    raise NoOpportunityRemain

                if self.appear(STAGE_DETAILED_CHECK, offset=(5, 5), static=False) \
                        and not self.appear(FIGHT, threshold=25) \
                        and confirm_timer.reached():
                    raise NoOpportunityRemain
        else:
            while 1:
                if skip_first_screenshot:
                    skip_first_screenshot = False
                else:
                    self.device.screenshot()

                if click_timer_2.reached() and self.appear(STAGE_CHECK, offset=(5, 5),
                                                           static=False) and not self.appear(STAGE_DETAILED_CHECK,
                                                                                             offset=(5, 5),
                                                                                             static=False):
                    self.device.click_minitouch(*stage.location)
                    logger.info('Click %s @ %s' % (point2str(*stage.location), 'STAGE'))
                    confirm_timer.reset()
                    click_timer_2.reset()
                    continue

                if click_timer.reached() and self.appear_then_click(FIGHT, interval=1, static=False):
                    self.device.sleep(6)
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if click_timer.reached() and self.handle_event(1):
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if click_timer.reached() and self.appear_then_click(AUTO_SHOOT, offset=(30, 30), interval=5,
                                                                    threshold=0.8, static=False):
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if click_timer.reached() and self.appear_then_click(AUTO_BURST, offset=(30, 30), interval=5,
                                                                    threshold=0.8, static=False):
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if click_timer.reached() and self.appear_then_click(NEXT_STAGE, offset=(30, 30), static=False):
                    self.device.sleep(3)
                    confirm_timer.reset()
                    click_timer.reset()
                    continue

                if click_timer.reached() \
                        and not self.appear(NEXT_STAGE, offset=(30, 30), static=False) \
                        and self.appear_then_click(END_CHECK, offset=(30, 30), static=False):
                    self.ensure_back()
                    break

                if click_timer.reached() and self.appear(PAUSE, offset=(30, 30)):
                    confirm_timer.reset()
                    click_timer.reset()
                    self.device.sleep(5)
                    continue

                if self.appear(STAGE_DETAILED_CHECK, offset=(5, 5), static=False) \
                        and not self.appear(FIGHT) \
                        and confirm_timer.reached():
                    raise NoOpportunityRemain

        self.ensure_opportunity_remain()

    def ensure_back(self, skip_first_screenshot=True):
        confirm_timer = Timer(1, count=3).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(HARD_AVAILABLE_CHECK, offset=(5, 5), interval=1,
                                                                static=False):
                raise HardEventAvailable

            if click_timer.reached() and self.handle_event(1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(END_CHECK, offset=(30, 30), interval=1, static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear(STAGE_CHECK, offset=(30, 30), static=False) and not self.appear(
                    GOTO_BACK, offset=(30, 30), static=False):
                self.device.click_minitouch(100, 100)
                logger.info('Click %s @ %s' % (point2str(100, 100), 'BACK'))
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(GOTO_BACK, offset=(30, 30), static=False) and confirm_timer.reached():
                break

    def ensure_opportunity_remain(self):
        if self.appear(self.no_opportunity, offset=(5, 5), threshold=0.95, static=False):
            raise NoOpportunityRemain

    def crop(self, area):
        self.device.screenshot()
        return crop(self.device.image, area)
