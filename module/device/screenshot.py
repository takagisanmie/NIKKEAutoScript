from functools import cached_property

from module.base.timer import Timer
from module.base.utils import image_size
from module.device.method.droidcast import DroidCast
from module.exception import RequestHumanTakeover


class Screenshot(DroidCast):
    _screenshot_interval = Timer(1.3)

    @cached_property
    def screenshot_methods(self):
        return {
            'DroidCast': self.screenshot_droidcast,
        }

    def screenshot(self):
        """
            截图

            Returns:
                np.ndarray:
        """
        self._screenshot_interval.wait()
        self._screenshot_interval.reset()

        method = self.screenshot_methods.get(self.config.Emulator_ScreenshotMethod)
        self.image = method()

        self.image = self._handle_orientated_image(self.image)

        return self.image

    def _handle_orientated_image(self, image):
        """
            Args:
                image (np.ndarray):

            Returns:
                np.ndarray:
        """
        width, height = image_size(self.image)
        if width == 720 and height == 1280:
            return image

        raise RequestHumanTakeover
