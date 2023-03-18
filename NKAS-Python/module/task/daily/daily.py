import glo
from common.exception import Timeout
from module.base.task import Task
from module.task.daily.daily_assets import *
from module.tools.timer import Timer
from module.ui.page import *
from module.ui.ui import UI


class Daily(UI, Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.equipmentUpgrade = int(self.config.get('Task.Daily.equipmentUpgrade', self.config.Task_Dict))
        self.nikkeUpgrade = int(self.config.get('Task.Daily.nikkeUpgrade', self.config.Task_Dict))
        self.notification = int(self.config.get('Notification', self.config.dict))

    def run(self):

        self.LINE('Daily')
        self.to_mail()
        if self.equipmentUpgrade:
            self.improve_equipment()
        glo.getNKAS().reward()
        self.go(destination=page_daily)
        self.getReward()
        self.to_pass()
        self.to_liberation()
        self.finish(self.config, 'Daily', second=60)
        self.INFO('Daily is finished')
        self.notice()
        self.go(page_main)

    def notice(self):
        from winotify import Notification
        from win10toast import ToastNotifier

        if self.notification == 1:
            toast = ToastNotifier()
            toast.show_toast(title="NKAS", msg="任务已全部完成！",
                             icon_path=r"./common/ico/Helm-Circle.ico", duration=10)

        elif self.notification == 2:
            ico_path = __file__
            ico_path = ico_path.replace('module\\task\\daily\\daily.py', '')
            toast = Notification(app_id="NKAS",
                                 title="NKAS",
                                 msg="任务已全部完成！",
                                 icon=f'{ico_path}common\ico\Helm-Circle.ico', duration='long')

            toast.show()

    def getReward(self):
        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=8).start()
        reset_timer = Timer(1, count=8).start()
        click_timer = Timer(1.2)

        glo.set_value('getReward', [])
        mask_id = 'getReward'

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.appear_then_click(reward, value=0.8):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(get):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(emphasis, img_template=emphasis_area,
                                                                       mask_id=mask_id):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                return

            if reset_timer.reached():
                reset_timer.reset()
                glo.set_value(mask_id, [])

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def improve_equipment(self):
        self.go(destination=page_inventory)
        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=3).start()
        reset_timer = Timer(1, count=8).start()
        click_timer = Timer(1.2)

        glo.set_value('improve_equipment', [])
        mask_id = 'improve_equipment'

        is_finished = False

        while 1:
            self.device.screenshot()

            if not is_finished and click_timer.reached() and self.device.appear_then_click(equipment, mask_id=mask_id):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if self.device.appear(nothing):
                return

            if not is_finished \
                    and click_timer.reached() \
                    and self.device.appear(inventory_sign) \
                    and self.device.appear_then_click(Level_0, once=True, img_template=inventory_area):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not is_finished and click_timer.reached() and self.device.appear_then_click(improve):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(confirm_improvement):
                is_finished = True
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if not is_finished and click_timer.reached() \
                    and (self.device.appear_then_click(normal_materials)
                         or self.device.appear_then_click(advanced_materials)):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if is_finished and click_timer.reached() and self.device.appear_then_click(close_equipment):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if is_finished and self.device.appear(inventory_sign) and confirm_timer.reached():
                return

            if reset_timer.reached():
                reset_timer.reset()
                glo.set_value(mask_id, [])

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def to_liberation(self):
        self.go(page_liberation)

        timeout = Timer(20).start()
        confirm_timer = Timer(3, count=5).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()

            if click_timer.reached() and self.device.clickTextLocation('完成'):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def to_pass(self):
        self.go(page_pass)

        timeout = Timer(20).start()
        confirm_timer = Timer(3, count=5).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()
            if click_timer.reached() \
                    and self.device.appear(rank_up, value=0.8) \
                    and self.device.uiautomator_click(360, 820):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(reward, value=0.8):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(pass_get):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(pass_mission):
                timeout.reset()
                click_timer.reset()

            if click_timer.reached() and self.device.appear_then_click(pass_reward):
                timeout.reset()
                click_timer.reset()

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def to_mail(self):
        self.go(page_mail)

        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=5).start()
        click_timer = Timer(1.2)

        while 1:
            self.device.screenshot()
            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(mail_get):
                timeout.reset()
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                return

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout
