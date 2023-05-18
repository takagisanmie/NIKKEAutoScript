from functools import cached_property

import cv2

from module.base.button import Button
from module.base.timer import Timer
from module.base.utils import exec_file, color_similar, get_color, find_center
from module.logger import logger
from module.map.map_grids import SelectedGrids
from module.ui.ui import UI


class Category(UI):
    def __init__(self, button, _active, _inactive, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button = button
        self._active = _active
        self._inactive = _inactive

    @cached_property
    def image_gray(self):
        self.button.ensure_template()
        self.button.image = cv2.cvtColor(self.button.image, cv2.COLOR_BGR2GRAY)
        return self.button.image

    @property
    def area(self) -> tuple:
        if isinstance(self.button, tuple):
            return self.button
        elif isinstance(self.button, Button):
            _ = self.image_gray
            image_gray = cv2.cvtColor(self.device.image, cv2.COLOR_BGR2GRAY)
            if self.button.match(image_gray, offset=(5, 5), static=False):
                return self.button.button

    @property
    def activated(self) -> bool:
        if self.area:
            return color_similar(get_color(self.device.image, self.area), self._active)
        else:
            logger.warning(f"Button '{self.button.name}' is not available")

    @property
    def inactivated(self) -> bool:
        if self.area:
            return color_similar(get_color(self.device.image, self.area), self._inactive)
        else:
            logger.warning(f"Button '{self.button.name}' is not available")

    def click(self):
        self.device.click_minitouch(*find_center(self.area))

    def ensure_is_visible(self, skip_first_screenshot=True):
        scroll_timer = Timer(0, count=4).start()
        click_timer = Timer(0.3)
        self.ensure_sroll_to_top(x1=(450, 870), x2=(450, 1200), delay=0.6)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.area is not None:
                break

            if not scroll_timer.reached(increase=False) and click_timer.reached():
                self.device.swipe((450, 1200), (450, 1170), handle_control_check=False)
                self.device.sleep(1)
                scroll_timer.reached()
                click_timer.reset()
                continue

            if scroll_timer.reached(increase=False):
                raise


class NIKKE:
    def __init__(self, name, _class, weapon, company, element, button):
        self.name = name
        self._class = _class
        self.weapon = weapon
        self.company = company
        self.element = element
        self.button = button

    def __str__(self):
        return f'NIKKE({self.name},{self.weapon},{self._class},{self.company},{self.element})'


class NIKKESwitch(UI):
    assets = './module/nikke_switch/assets.py'
    _nikke_info = './module/nikke_switch/nikke_info.py'

    def __init__(self, list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list = list

    @cached_property
    def nikke_info(self) -> list[dict]:
        return [i for i in exec_file(self._nikke_info).values() if i.get('name').upper() in self.list]

    @cached_property
    def nikke_list(self):
        return SelectedGrids(
            [NIKKE(*[i.values() for i in self.nikke_info if i.get('name').upper() == k][0], v) for k, v in
             exec_file(self.assets).items() if
             k in self.list])
