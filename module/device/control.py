from functools import cached_property

from module.base.button import Button
from module.base.utils import ensure_int, point2str, rectangle_point
from module.device.method.minitouch import Minitouch
from module.logger import logger


class Control(Minitouch):
    def handle_control_check(self, button):
        # Will be overridden in Device
        pass

    @cached_property
    def click_methods(self):
        return {
            'minitouch': self.click_minitouch,
        }

    def click(self, button: Button, control_check=True):
        """Method to click a button.

        Args:
            button (button.Button): AzurLane Button instance.
            control_check (bool):
        """
        if control_check:
            self.handle_control_check(button)

        # x, y = random_rectangle_point(button.button)
        x, y = rectangle_point(button.button)

        x, y = ensure_int(x, y)
        logger.info(
            'Click %s @ %s' % (point2str(x, y), button)
        )
        method = self.click_methods.get(
            self.config.Emulator_ControlMethod)
        method(x, y)
