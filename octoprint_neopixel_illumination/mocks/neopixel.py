import http.client
import json
import logging
import socket
import time
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


def get_logger():
    return logging.getLogger("octoprint.plugins.neopixel_illumination.api.neopixel")


class NeoPixelDelegate:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def init(self, config):
        pass

    def show(self):
        pass

    def fill(self, r: int, g: int, b: int, w: int):
        pass

    def set_item(self, index: int, r: int, g: int, b: int, w: int):
        pass

    def get_item(self, index: int):
        pass

    def set_brightness(self, brightness: float):
        pass

    def get_brightness(self):
        pass


class LoggingNeoPixelDelegate(NeoPixelDelegate):
    def init(self, config):
        self._logger.info(f"config {json.dumps(config)}")

    def show(self):
        self._logger.info("show")

    def fill(self, r: int, g: int, b: int, w: int):
        self._logger.info(f"fill {r, g, b, w}")

    def set_item(self, index: int, r: int, g: int, b: int, w: int):
        self._logger.info(f"set {index} {r, g, b, w}")

    def get_item(self, index: int):
        self._logger.info(f"get")

    def set_brightness(self, brightness: float):
        self._logger.info(f"brightness {brightness}")

    def get_brightness(self):
        self._logger.info(f"brightness")


class HttpNeoPixelDelegate(NeoPixelDelegate):
    JSON_HEADERS = {"Content-type": "application/json"}

    def __init__(self, api_host, logger):
        super().__init__(logger)
        self._config = None
        self._neopixel_api = http.client.HTTPConnection(api_host)

    def init(self, config):
        self._config = config
        self._post("/create", json.dumps(self._config), self.JSON_HEADERS)

    def _post(self, url: str, body: str, headers: dict):
        try:
            self._neopixel_api.request("POST", url, body, headers)
            return self._neopixel_api.getresponse()
        except ConnectionRefusedError:
            self._logger.exception(
                f"NeoPixel API is not available at `{self._neopixel_api.host}`"
            )

        return None

    def _get(self, url: str):
        try:
            self._neopixel_api.request("GET", url)
            return self._neopixel_api.getresponse()
        except ConnectionRefusedError:
            self._logger.error(
                f"NeoPixel API is not available at `{self._neopixel_api.host}`"
            )

        return None

    def show(self):
        self._get("/show")

    def fill(self, r: int, g: int, b: int, w: int):
        self._get(f"/fill/{r},{g},{b},{w}")

    def set_item(self, index: int, r: int, g: int, b: int, w: int):
        self._get(f"/pixel/{index}/{r},{g},{b},{w}")

    def get_item(self, index: int):
        self._get(f"/pixel/{index}")

    def set_brightness(self, brightness: float):
        self._get(f"/brightness/{brightness}")

    def get_brightness(self):
        self._get(f"/brightness")


class SocketNeoPixelDelegate(NeoPixelDelegate):
    def __init__(self, server_address, logger):
        super().__init__(logger)
        self._client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self._client.connect(server_address)
        except ConnectionRefusedError:
            self._logger.error("Connection refused: {}".format(server_address))

    def _send(self, data: dict):
        message = json.dumps(data)
        try:
            self._client.send(message.encode() + b"\n")
        except (BrokenPipeError, OSError) as e:
            self._logger.error("{}: {}".format(e, self._client))

    def init(self, config: dict):
        self._send({"init": config})

    def show(self):
        self._send({"show": ""})

    def fill(self, r: int, g: int, b: int, w: int):
        self._send({"fill": (r, g, b, w)})

    def set_item(self, index: int, r: int, g: int, b: int, w: int):
        self._send({"pixel": [index, (r, g, b, w)]})

    def set_brightness(self, brightness: float):
        self._send({"brightness": brightness})


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
        delegate: NeoPixelDelegate = None,
    ):
        self._pin = pin
        self._pixels = n
        self._bpp = bpp
        self._brightness = brightness
        self._auto_write = auto_write
        self._pixel_order = pixel_order

        self._config = {
            "pin": pin.id,
            "n": n,
            "brightness": brightness,
            "pixel_order": pixel_order,
        }

        self._pixel_buffer = [(0, 0, 0, 0) for _ in range(n)]

        self._delegate: NeoPixelDelegate = delegate or LoggingNeoPixelDelegate(get_logger())
        self._delegate.init(self._config)

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    @property
    def brightness(self):
        self._delegate.get_brightness()
        return self._brightness

    @brightness.setter
    def brightness(self, value: float):
        self._brightness = value
        self._delegate.set_brightness(value)

    def show(self):
        self._delegate.show()

    def fill(self, color: ColorUnion):
        r, g, b, w = color
        self._delegate.fill(r, g, b, w)
        # for i in range(self._pixels):
        #     self._set_item(i, r, g, b, w)
        # if self._auto_write:
        #     self.show()

    def __len__(self):
        return self._pixels

    def _set_item(self, index: int, r: int, g: int, b: int, w: int):
        if index < 0:
            index += len(self)
        if index >= self._pixels or index < 0:
            raise IndexError

        # self._pixel_buffer[index] = (r, g, b, w)
        self._delegate.set_item(index, r, g, b, w)

    def __setitem__(
        self, index: Union[int, slice], val: Union[ColorUnion, Sequence[ColorUnion]]
    ):
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
        self._delegate.get_item(index)
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


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return r, g, b, 0


def demo(neopixel: NeoPixel):
    num_pixels = int(len(neopixel))

    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            neopixel[i] = wheel(pixel_index & 255)
        neopixel.show()
        time.sleep(0.001)
