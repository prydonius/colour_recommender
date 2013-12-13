'''
py-color-classifier
Copyright (C) 2011  Joar Wandborg

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import logging

from colormath.color_objects import LabColor, RGBColor

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.ERROR)


class Classifier():
    '''
    Classifier

    Example:
        >>> classifier = Classifier(rgb=[255, 170, 0])
        >>> classifier.get_name()
        'orange'
    '''
    lab = LabColor

    '''
    TODO - Make colors easily extensible
    '''
    colors = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "lightgray": (211, 211, 211),
        "gray": (169, 169, 169),
        "darkgray": (105, 105, 105),
        # Red
        "salmon": (250, 128, 114),
        "red": (255, 0, 0),
        "maroon": (128, 0, 0),
        # Orange
        "orange": (255, 165, 0),
        "darkorange": (255, 140, 0),
        "rosybrown": (188, 143, 143),
        "saddlebrown": (139, 69, 19),
        # Yellow
        "khaki": (240, 230, 140),
        "yellow": (255, 255, 0),
        "gold": (255, 215, 0),
        # Green
        "lawngreen": (124, 252, 0),
        "lightgreen": (50, 205, 50),
        "green": (34, 139, 34),
        "darkgreen": (0, 100, 0),
        "seagreen": (46, 139, 87),
        "teal": (0, 128, 128),
        # Cyan
        "cyan": (0, 255, 255),
        # Blues
        "steelblue": (70, 130, 180),
        "lightblue": (135, 206, 250),
        "midnightblue": (25, 25, 112),
        "blue": (0, 0, 255),
        # Purples
        "indigo": (75, 0, 130),
        "lightpurple": (147, 112, 219),
        "purple": (128, 0, 128),
        # Pinks
        "magenta": (255, 0, 255),
        "deeppink": (255, 20, 147),
        "lightpink": (255, 192, 203)
    }

    colors_lab = dict()

    def __init__(self, **kwargs):
        if kwargs.get('rgb'):
            self.set_rgb(kwargs.get('rgb'))

    def set_rgb(self, rgb):
        '''
        Pass an RGB value to the classifier
        '''
        rgb = RGBColor(*rgb)
        logger.debug(rgb.get_rgb_hex())
        self.lab = rgb.convert_to('lab')
        logger.debug('Saved lab: {lab} from rgb: {rgb}'.format(
                lab=self._lab_to_tuple(self.lab),
                rgb=rgb))
        self._update_lab_colors()

    def _update_lab_colors(self):
        for name, val in self.colors.items():
            self.colors_lab.update({
                    name: self._lab_to_tuple(
                        self._rgb_to_lab(
                            list(
                                val)))})
        logger.debug('colors_lab: %1s' % self.colors_lab)
        return True

    def get_name(self):
        '''
        Get color name from the classifier.
        '''
        (name, values) = min(self.colors_lab.items(),
            key=ColorDistance(self._lab_to_tuple(self.lab)))
        return name

    def getColourName(self, color):
        self.set_rgb(color)
        return self.get_name()

    def _lab_to_tuple(self, lab):
        return (lab.lab_l, lab.lab_a, lab.lab_b)

    def _rgb_to_lab(self, rgb):
        rgb = RGBColor(*rgb)
        return rgb.convert_to('lab')

    def getColours(self):
        return self.colors;


class ColorDistance(object):
    '''
    Calculates the distance between 3-tuples with numbers

    Example:
    min(
        dict(
            black=(0, 0, 0),
            red=(255, 0, 0),
            blue=(0, 0, 255)
        ).items(),
        key=ColorDistance((255, 0, 0))
    '''
    def __init__(self, color):
        self.color = color

    def __call__(self, item):
        return self.distance(self.color, item[1])

    def distance(self, left, right):
        return sum((l - r) ** 2 for l, r in zip(left, right)) ** 0.5


if __name__ == '__main__':
    c = Classifier(rgb=[198, 224, 255])
    print(c.get_name())
    c.set_rgb([255, 0, 0])
    print(c.get_name())
    c.set_rgb([255, 170, 0])
    print(c.get_name())
    c.set_rgb([0, 0, 0])
    print(c.get_name())
    c.set_rgb([0, 173, 255])
    print(c.get_name())
