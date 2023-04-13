import os
from functools import cached_property

import cv2
import imageio
import numpy as np

from module.base.resource import Resource
from module.base.utils import crop, load_image, area_offset, color_similar, get_color


class Button(Resource):
    def __init__(self, area, color, button, file=None, name=None):
        """Initialize a Button instance.

        Args:
            area (dict[tuple], tuple): Area that the button would appear on the image.
                          (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
            color (dict[tuple], tuple): Color we expect the area would be.
                           (r, g, b)
            button (dict[tuple], tuple): Area to be click if button appears on the image.
                            (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
                            If tuple is empty, this object can be use as a checker.
        Examples:
            BATTLE_PREPARATION = Button(
                area=(1562, 908, 1864, 1003),
                color=(231, 181, 90),
                button=(1562, 908, 1864, 1003)
            )
        """
        self.raw_area = area
        self.raw_color = color
        self.raw_button = button
        self.raw_file = file
        self.raw_name = name

        self._button_offset = None
        self._match_init = False
        self._match_binary_init = False
        self._match_luma_init = False
        self.image = None
        self.image_binary = None
        self.image_luma = None

        if self.file:
            self.resource_add(key=self.file)

    @cached_property
    def name(self):
        if self.raw_name:
            return self.raw_name
        elif self.file:
            return os.path.splitext(os.path.split(self.file)[1])[0]
        else:
            return 'BUTTON'

    @cached_property
    def file(self):
        return self.parse_property(self.raw_file)

    @cached_property
    def area(self):
        return self.parse_property(self.raw_area)

    @cached_property
    def color(self):
        return self.parse_property(self.raw_color)

    @cached_property
    def _button(self):
        return self.parse_property(self.raw_button)

    @property
    def button(self):
        if self._button_offset is None:
            return self._button
        else:
            return self._button_offset

    @property
    def location(self):
        x = (self.button[0] + self.button[2]) / 2
        y = (self.button[1] + self.button[3]) / 2
        return x, y

    @cached_property
    def is_gif(self):
        if self.file:
            return os.path.splitext(self.file)[1] == '.gif'
        else:
            return False

    def __str__(self):
        return self.name

    def ensure_template(self):
        """
        Load asset image.
        If needs to call self.match, call this first.
        """
        if not self._match_init:
            if self.is_gif:
                self.image = []
                for image in imageio.mimread(self.file):
                    image = image[:, :, :3].copy() if len(image.shape) == 3 else image
                    image = crop(image, self.area)
                    self.image.append(image)
            else:
                self.image = load_image(self.file, self.area)
            self._match_init = True

    def match(self, image, offset=30, threshold=0.85, static=True) -> bool:
        self.ensure_template()

        if static:
            if isinstance(offset, tuple):
                if len(offset) == 2:
                    offset = np.array((-offset[0], -offset[1], offset[0], offset[1]))
                else:
                    offset = np.array(offset)
            else:
                offset = np.array((-3, -offset, 3, offset))

            image = crop(image, offset + self.area)

        res = cv2.matchTemplate(self.image, image, cv2.TM_CCOEFF_NORMED)
        _, similarity, _, upper_left = cv2.minMaxLoc(res)
        # print(self.name, similarity)

        if static:
            self._button_offset = area_offset(self._button, offset[:2] + np.array(upper_left))
        else:
            h, w = self.area[3] - self.area[1], self.area[2] - self.area[0]
            bottom_right = (upper_left[0] + w, upper_left[1] + h)
            self._button_offset = (upper_left[0], upper_left[1], bottom_right[0], bottom_right[1])

        return similarity > threshold

        # if self.is_gif:
        #     for template in self.image:
        #         res = cv2.matchTemplate(template, image, cv2.TM_CCOEFF_NORMED)
        #         _, similarity, _, point = cv2.minMaxLoc(res)
        #         self._button_offset = area_offset(self._button, offset[:2] + np.array(point))
        #         if similarity > threshold:
        #             return True
        #     return False
        # else:

    def appear_on(self, image, threshold=10) -> bool:
        """Check if the button appears on the image.

        Args:
            image (np.ndarray): Screenshot.
            threshold (int): Default to 10.

        Returns:
            bool: True if button appears on screenshot.
        """
        return color_similar(
            color1=get_color(image, self.area),
            color2=self.color,
            threshold=threshold
        )

    def match_appear_on(self, image, threshold=30) -> bool:
        """
        Args:
            image: Screenshot.
            threshold: Default to 10.

        Returns:
            bool:
        """
        diff = np.subtract(self.button, self._button)[:2]
        area = area_offset(self.area, offset=diff)
        return color_similar(color1=get_color(image, area), color2=self.color, threshold=threshold)
