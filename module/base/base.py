from module.base.button import Button
from module.base.timer import Timer
from module.config.config import NikkeConfig
from module.device.device import Device
from module.logger import logger


class ModuleBase:
    config: NikkeConfig
    device: Device

    def __init__(self, config, device=None, task=None):
        """
              Args:
                  config (AzurLaneConfig, str):
                      Name of the user config under ./config
                  device (Device):
                      To reuse a device.
                      If None, create a new Device object.
                      If str, create a new Device object and use the given device as serial.
                  task (str):
                      Bind a task only for dev purpose. Usually to be None for auto task scheduling.
                      If None, use default configs.
              """
        if isinstance(config, NikkeConfig):
            self.config = config
        elif isinstance(config, str):
            self.config = NikkeConfig(config, task=task)
        else:
            logger.warning('NKAS ModuleBase received an unknown config, assume it is NikkeConfig')
            self.config = config

        if isinstance(device, Device):
            self.device = device
        elif device is None:
            self.device = Device(config=self.config)
        elif isinstance(device, str):
            self.config.override(Emulator_Serial=device)
            self.device = Device(config=self.config)
        else:
            logger.warning('NKAS ModuleBase received an unknown device, assume it is Device')
            self.device = device

        self.interval_timer = {}

    def appear(self, button: Button, offset=0, interval=0, threshold=None, static=True) -> bool:

        self.device.stuck_record_add(button)

        if interval:
            if button.name in self.interval_timer:
                if self.interval_timer[button.name].limit != interval:
                    self.interval_timer[button.name] = Timer(interval)
            else:
                self.interval_timer[button.name] = Timer(interval)
            if not self.interval_timer[button.name].reached():
                return False

        if offset:
            if isinstance(offset, bool):
                offset = self.config.BUTTON_OFFSET

            appear = button.match(self.device.image, offset=offset,
                                  threshold=self.config.BUTTON_MATCH_SIMILARITY if not threshold else threshold,
                                  static=static)
        else:
            appear = button.appear_on(self.device.image,
                                      threshold=self.config.COLOR_SIMILAR_THRESHOLD if not threshold else threshold)

        if appear and interval:
            self.interval_timer[button.name].reset()

        return appear

    def appear_then_click(self, button, screenshot=False, offset=0, interval=0, threshold=None,
                          static=True) -> bool:

        appear = self.appear(button, offset=offset, interval=interval, threshold=threshold, static=static)
        if appear:
            if screenshot:
                self.device.sleep(self.config.WAIT_BEFORE_SAVING_SCREEN_SHOT)
                self.device.screenshot()
            self.device.click(button)

        return appear

    def appear_text(self, text, interval=0) -> bool or tuple:
        if interval:
            if text in self.interval_timer:
                if self.interval_timer[text].limit != interval:
                    self.interval_timer[text] = Timer(interval)
            else:
                self.interval_timer[text] = Timer(interval)
            if not self.interval_timer[text].reached():
                return False

        res = self.device.ocr(self.device.image)
        res = self.device.filter(res)
        location = self.device.get_location(text, res)
        if location:
            if interval:
                self.interval_timer[text].reset()
            return location
        else:
            return False

    def appear_then_click_text(self, text, interval=0) -> bool:
        location = self.appear_text(text, interval)
        if location:
            self.device.click_minitouch(location[0], location[1])
            return True
        else:
            return False
