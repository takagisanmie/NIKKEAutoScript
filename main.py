import time
from datetime import datetime, timedelta
from functools import cached_property

import inflection

import glo
from module.config.config import NikkeConfig, TaskEnd
from module.config.utils import deep_get, deep_set
from module.exception import RequestHumanTakeover, GameNotRunningError, GameStuckError, GameTooManyClickError, \
    GameServerUnderMaintenance, GameStart
from module.handler.assets import CONFRIM_B, CONFRIM_C
from module.logger import logger


class NikkeAutoScript:
    def __init__(self, config_name='nkas'):
        glo._init()
        glo.set_value('nkas', self)
        logger.hr('Start', level=0)
        self.config_name = config_name

    @cached_property
    def config(self):
        try:
            config = NikkeConfig(config_name=self.config_name)
            return config
        except RequestHumanTakeover:
            logger.critical('Request human takeover')
            exit(1)
        except Exception as e:
            logger.exception(e)
            exit(1)

    @cached_property
    def device(self):
        try:
            from module.device.device import Device
            device = Device(config=self.config)
            return device
        except RequestHumanTakeover:
            logger.critical('Request human takeover')
            exit(1)
        except Exception as e:
            logger.exception(e)
            exit(1)

    def run(self, command):
        try:
            self.device.screenshot()
            self.__getattribute__(command)()
            return True

        except TaskEnd:
            return True

        except GameStart:
            self.start()
            return True

        except GameNotRunningError as e:
            logger.warning(e)
            self.config.task_call('Restart')
            return True

        except (GameStuckError, GameTooManyClickError) as e:
            '''
                当一直没有进行操作时或点击同一目标过多时，尝试重启游戏
            '''
            logger.error(e)
            '''
                self.save_error_log()
                在 Alas 中会将在raise前最后的截图和log写入./log/error 
            '''
            logger.warning(f'Game stuck, {self.device.package} will be restarted in 10 seconds')
            logger.warning('If you are playing by hand, please stop NKAS')
            self.config.task_call('Restart')
            self.device.sleep(10)
            return False

        except GameServerUnderMaintenance as e:
            logger.error(e)
            self.device.app_stop()
            exit(1)

        except RequestHumanTakeover:
            logger.critical('Request human takeover')
            exit(1)

        except Exception as e:
            logger.exception(e)
            exit(1)

    def restart(self):
        from module.handler.login import LoginHandler
        LoginHandler(self.config, device=self.device).app_restart()

    def start(self):
        from module.handler.login import LoginHandler
        LoginHandler(self.config, device=self.device).app_start()

    def goto_main(self):
        from module.handler.login import LoginHandler
        from module.ui.ui import UI
        if self.device.app_is_running():
            logger.info('App is already running, goto main page')
            UI(self.config, device=self.device).ui_goto_main()
        else:
            logger.info('App is not running, start app and goto main page')
            LoginHandler(self.config, device=self.device).app_start()
            UI(self.config, device=self.device).ui_goto_main()

    def reward(self):
        from module.reward.reward import Reward
        Reward(config=self.config, device=self.device).run()

    def destroy(self):
        from module.destroy.destroy import Destroy
        Destroy(config=self.config, device=self.device).run()

    def commission(self):
        from module.commission.commission import Commission
        Commission(config=self.config, device=self.device).run()

    def conversation(self):
        from module.conversation.conversation import Conversation
        Conversation(config=self.config, device=self.device).run()

    def rookie_arena(self):
        from module.rookie_arena.rookie_arena import RookieArena
        RookieArena(config=self.config, device=self.device).run()

    def simulation_room(self):
        from module.simulation_room.simulation_room import SimulationRoom
        SimulationRoom(config=self.config, device=self.device).run()

    def wait_until(self, future):
        """
            Wait until a specific time.

            Args:
                future (datetime):

            Returns:
                bool: True if wait finished, False if config changed.
        """
        future = future + timedelta(seconds=1)
        '''
            记录开始等待任务时，配置文件的最后更改时间
        '''
        self.config.start_watching()
        while 1:
            if datetime.now() > future:
                return True

            # if self.stop_event is not None:
            #     if self.stop_event.is_set():
            #         logger.info("Update event detected")
            #         logger.info(f"[{self.config_name}] exited. Reason: Update")
            #         exit(0)

            time.sleep(5)
            '''
                在等待过程中持续对比配置文件的最后更改时间
            '''
            if self.config.should_reload():
                return False

    def get_next_task(self):
        """
            Returns:
                str: Name of the next task.
        """
        while 1:
            task = self.config.get_next()
            self.config.task = task
            '''
                在 Alas 中每个任务都有共有属性 Scheduler
                调度器在运行任务时，是根据任务的 Scheduler.Command 调用对应方法
                在那之前，Alas 会调用 config.bind(task)
                将该任务的 Scheduler 属性覆盖到类变量
                在使用到共有属性时，只会使用该任务的设置
                例如在设置任务的下次运行时间时，会使用到 Scheduler.SuccessInterval
                interval = (self.Scheduler_SuccessInterval if success else self.Scheduler_FailureInterval)
                run.append(datetime.now() + ensure_delta(interval))
            '''
            self.config.bind(task)
            from module.base.resource import release_resources
            if self.config.task.command != 'NKAS':
                release_resources(next_task=task.command)

            if task.next_run > datetime.now():
                logger.info(f'Wait until {task.next_run} for task `{task.command}`')
                method = self.config.Optimization_WhenTaskQueueEmpty

                '''
                    在等待任务的过程中可能会被人为修改运行时间
                    if not self.wait_until(task.next_run):
                        del self.__dict__['config']
                        continue
                        
                    Returns:
                        bool: True if wait finished, False if config changed.
                '''

                if method == 'close_game':
                    logger.info('Close game during wait')
                    self.device.app_stop()
                    release_resources()
                    if not self.wait_until(task.next_run):
                        del self.__dict__['config']
                        continue
                    self.run('start')
                elif method == 'goto_main':
                    logger.info('Goto main page during wait')
                    self.run('goto_main')
                    release_resources()
                    if not self.wait_until(task.next_run):
                        del self.__dict__['config']
                        continue
                elif method == 'stay_there':
                    logger.info('Stay there during wait')
                    release_resources()
                    if not self.wait_until(task.next_run):
                        del self.__dict__['config']
                        continue
            break

        return task.command

    def loop(self):
        logger.set_file_logger(self.config_name)
        logger.info(f'Start scheduler loop: {self.config_name}')
        is_first = True
        failure_record = {}

        while 1:
            task = self.get_next_task()
            _ = self.device

            if is_first and task == 'Restart':
                logger.info('Skip task `Restart` at scheduler start')
                self.config.task_delay(server_update=True)
                del self.__dict__['config']
                continue

            # Run
            logger.info(f'Scheduler: Start task `{task}`')
            self.device.stuck_record_clear()
            self.device.click_record_clear()
            logger.hr(task, level=0)
            '''
            
                https://inflection.readthedocs.io/en/latest/
                
                inflection.underscore('Restart') => 'restart'
                inflection.underscore('DeviceType') => 'device_type'
                
            '''
            success = self.run(inflection.underscore(task))
            logger.info(f'Scheduler: End task `{task}`')
            is_first = False

            '''
                记录某个任务出错的次数
            '''
            failed = deep_get(failure_record, keys=task, default=0)
            failed = 0 if success else failed + 1
            deep_set(failure_record, keys=task, value=failed)
            if failed >= 3:
                logger.critical(f"Task `{task}` failed 3 or more times.")
                logger.critical("Possible reason #1: You haven't used it correctly. "
                                "Please read the help text of the options.")
                logger.critical("Possible reason #2: There is a problem with this task. "
                                "Please contact developer or try to fix it yourself.")
                logger.critical('Request human takeover')
                exit(1)

            if success:
                del self.__dict__['config']
                continue
            # 出现错误时
            else:
                del self.__dict__['config']
                continue


from module.simulation_room.assets import *

if __name__ == '__main__':
    nkas = NikkeAutoScript()
    self = nkas
    self.device.screenshot()
    self.config.bind('Conversation')
    from module.simulation_room.simulation_room import SimulationRoom

    e = SimulationRoom(config=self.config, device=self.device)
    # e.choose_effect()
    # print(len(e.nikke_list))

    # e = SimulationRoom(config=self.config, device=self.device)
    #
    # if e.appear(MAX_EFFECT_COUNT, offset=(10, 10), static=False, threshold=0.96):
    #     print(111)

    # import uiautomator2 as u2
    # u2.connect_usb('')

    # a = self
    #
    self = e

    # _ = [(101, 122), (103, 123), (102, 121)]
    # _.sort(key=lambda x: x[1])
    # print(_[-1])
    # if self.appear(RANDOM_EVENT_CHECK, offset=(30, 30), static=False):
    #     from module.simulation_room.event import RandomEvent
    #     RandomEvent(button=RANDOM_EVENT_CHECK.location, config=self.config, device=self.device).run()
    from module.simulation_room.event import ImprovementEvent

    # RandomEvent(button=RANDOM_EVENT_CHECK.location, config=self.config, device=self.device).run()
    ImprovementEvent(button=IMPROVEMENT_EVENT_CHECK.location, config=self.config, device=self.device).run()
    if e.appear(RANDOM_EVENT_CHOOSE_EFFECT, offset=(10, 10), static=False, threshold=0.96):
        print(1)
    if e.appear(CONFRIM_B, offset=(30, 30), static=False):
        print(2)
    if e.appear(CONFRIM_C, offset=(30, 30), static=False):
        print(3)

    #
    # if e.appear(REPEATED_EFFECT_CHECK, offset=(5, 5), static=False):
    #     logger.warning('The selected effect has been in the own effect list')
    #     click_timer = Timer(0.3)
    #     while 1:
    #         self.device.screenshot()
    #
    #         if click_timer.reached() and e.appear_then_click(CANCEL, offset=(30, 30), interval=5,
    #                                                          static=False):
    #             click_timer.reset()
    #             continue
    #
    #         if click_timer.reached() and e.appear_then_click(NOT_CHOOSE, offset=(30, 30), interval=5,
    #                                                          static=False):
    #             click_timer.reset()
    #             continue
    #
    #         if click_timer.reached() and e.appear(SKIP_CHECK, offset=(30, 30), interval=5,
    #                                                  static=False):
    #             self.device.click_minitouch(530, 800)
    #             logger.info('Click %s @ %s' % (point2str(530, 800), 'SKIP'))
    #             click_timer.reset()
    #             continue
    #
    #         if e.appear(RESET_TIME_IN, offset=(30, 30), static=False):
    #             print(111)

    # print(NORMAL_CHECK.location)

    # self.device.screenshot()
    # ocr = OCR_MODEL.nikke
    # print(ocr.ocr(self.device.image))
    # for i in ENEMY_EVENT_CHECK.match_several(self.device.image, static=False)[:3]:
    #     area = i.get('area')
    #     area = _area_offset(area, (-45, -100, -14, -90))
    #     img = crop(self.device.image, area)
    #     if NORMAL_CHECK.match(img, threshold=0.75, static=False):
    #         print('normal', area)
    #     elif HARD_CHECK.match(img, threshold=0.75, static=False):
    #         print('hard', area)

    # e.appear_then_click(AUTO_SHOOT, offset=(30, 30), interval=1)
    # e.appear_then_click(AUTO_BURST, offset=(30, 30), interval=1)

    # OCR_OPPORTUNITY = DigitCounter(OCR_OPPORTUNITY, name='OCR_OPPORTUNITY', letter=(247, 247, 247), threshold=128)
    # print(OCR_OPPORTUNITY.ocr(self.device.image)[0])

    # ocr = OCR_MODEL.cnocr_gru.ocr
    #
    # answer_a_area = (82, 807, 640, 910)
    # answer_b_area = (82, 910, 640, 1010)
    #
    # answer_a = ocr(extract_letters(crop(self.device.image, answer_a_area), letter=(247, 243, 247)))
    # answer_b = ocr(extract_letters(crop(self.device.image, answer_b_area), letter=(247, 243, 247)))
    #
    # print(answer_a)
    # print(answer_b)

    #
    # list = '樱花 阿妮斯 麦斯威尔 舒格 白雪公主 伊莎贝尔 艾德米 吉萝婷 森 沃伦姆'
    # e = Conversation(config=self.config, device=self.device)
    # print(e.ensure_opportunity_remain())

    # r = [i.get('key') for i in Nikke_list if i.get('label') in '舒格']
    # print(Nikke_dialog.get(r[0]))

    # # print(e.config.Conversation_WaitToCommunicate)
    # opportunity = 10
    #
    # self.config.bind('Conversation')
    # e.run()
    # e.answer(None)

    # print(list.strip(' ').split(' '))
    # FAVOURITE_CHECK.ensure_template()
    # _ = FAVOURITE_CHECK.match(self.device.image, static=False)
    # if _:
    #     area = FAVOURITE_CHECK._button_offset
    #     name_area = _area_offset(area, (18, 57, 220, -10))
    #     check_area = _area_offset(area, (520, 57, 645, 12))
    #     rank_area = _area_offset(area, (28, 21, 150, -56))
    #
    #     _img = crop(self.device.image, name_area)
    #     _img = extract_letters(_img, letter=(74, 73, 74))
    #     text_rect = find_letter_area(_img < 128)
    #     text_rect = _area_offset(text_rect, (-2, -2, 3, 2))
    #     name = e.ocr(crop(_img, text_rect), 'NIKKE_NAME')
    #
    #     r = [i.get('key') for i in Nikke_list if i.get('label') in name]

    # e.ui_ensure(page_ark)

    # img = cv2.imread('./pic/Screenshot_20230405-233919.png')
    # img = cv2.imread('./pic/Screenshot_20230405-233936.png')
    # img = cv2.imread('./pic/Screenshot_20230411-120724.png')
    # img = cv2.imread('./pic/confirm1.png')
    # img = cv2.imread('./pic/confirm2.png')
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # e.device.image = img
    # CONFRIM_A 按钮为平面或立体，'确认'没有阴影
    # CONFRIM_B 按钮为立体，'确认'有阴影
    # e.device.screenshot()
    # e.handle_server()

    #
    # res = self.device.ocr(self.device.image)
    # print(res)
    # if e.appear_text('领取奖励'):
    #     logger.info('2')

    # save_image(self.device.image, f'./pic/{time.time()}-CONFRIM_A.png')
