from typing import Tuple, Union, Sequence

from .microcontroller import Pin

ColorUnion = Union[int, Tuple[int, int, int], Tuple[int, int, int, int]]

RGB = "RGB"
"""Red Green Blue"""
GRB = "GRB"
"""Green Red Blue"""
RGBW = "RGBW"
"""Red Green Blue White"""
GRBW = "GRBW"
"""Green Red Blue White"""


class NeoPixel:
    def __init__(
        self,
        pin: Pin,
        n: int,
        *,
        bpp: int = 3,
        brightness: float = 1.0,
        auto_write: bool = True,
        pixel_order: str = None,
    ):
        self._pin = pin
        self._pixels = n
        self._bpp = bpp
        self._brightness = brightness
        self._auto_write = auto_write
        self._pixel_order = pixel_order

        self._pixel_buffer = [(0, 0, 0, 0) for _ in range(n)]

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value: float):
        self._brightness = value

    def show(self):
        print(f"show ({', '.join([f'{idx}: {color}' for idx, color in enumerate(self._pixel_buffer)])})")

    def fill(self, color: ColorUnion):
        print(f"fill {color}")
        r, g, b, w = color
        for i in range(self._pixels):
            self._set_item(i, r, g, b, w)
        if self._auto_write:
            self.show()

    def __len__(self):
        return self._pixels

    def _set_item(self, index: int, r: int, g: int, b: int, w: int):
        if index < 0:
            index += len(self)
        if index >= self._pixels or index < 0:
            raise IndexError

        self._pixel_buffer[index] = (r, g, b, w)

    def __setitem__(self, index: Union[int, slice], val: Union[ColorUnion, Sequence[ColorUnion]]):
        if isinstance(index, slice):
            start, stop, step = index.indices(self._pixels)
            for val_i, in_i in enumerate(range(start, stop, step)):
                r, g, b, w = val[val_i]
                self._set_item(in_i, r, g, b, w)
        else:
            r, g, b, w = val
            self._set_item(index, r, g, b, w)

        if self._auto_write:
            self.show()

    def _getitem(self, index: int):
        return self._pixel_buffer[index]

    def __getitem__(self, index: Union[int, slice]):
        if isinstance(index, slice):
            out = []
            for in_i in range(*index.indices(len(self))):
                out.append(self._getitem(in_i))
            return out
        if index < 0:
            index += len(self)
        if index >= self._pixels or index < 0:
            raise IndexError
        return self._getitem(index)
