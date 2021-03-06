# coding=utf-8
from __future__ import absolute_import

import os
import subprocess
import sys

import octoprint.plugin

from .mocks import neopixel
from .mocks.microcontroller import Pin
from .mocks.neopixel import (
    HttpNeoPixelDelegate,
    LoggingNeoPixelDelegate,
    SocketNeoPixelDelegate,
    demo,
    wheel,
)

SOCKET_SERVER_ADDRESS = "/tmp/neopixel_socket"

BRIGHTNESS_KEY = "brightness"
COLOR_KEY = "color"
ENABLED_KEY = "enabled"
JSON_HEADERS = {"Content-type": "application/json"}
NEOPIXEL_API_HOST = "localhost:5001"
NEOPIXEL_API_HOST_KEY = "neopixel_api_host"
NEOPIXEL_API_SOCKET = "/tmp/neopixel_socket"
NUM_PIXELS_KEY = "num_pixels"
PARSE_GCODE_KEY = "parse_gcode"
PIXEL_ORDER_KEY = "pixel_order"
PIXEL_PIN_KEY = "pixel_pin"
SAVE_COLOR_COMMAND = "save_color"
SAVE_BRIGHTNESS_COMMAND = "save_brightness"
SET_COLOR_GCODE = "M150"
STARTUP_COLOR_KEY = "startup_color"
SUDO_DEFAULT_PASSWORD = "raspberry"
SUDO_PASSWORD_KEY = "sudo_password"
UPDATE_BRIGHTNESS_COMMAND = "update_brightness"
UPDATE_COLOR_COMMAND = "update_color"

PIXEL_ORDER_LIST = [
    neopixel.GRB,
    neopixel.GRBW,
    neopixel.RGB,
    neopixel.RGBW,
]

CONFIG_ITEMS = [
    ENABLED_KEY,
    NUM_PIXELS_KEY,
    PIXEL_ORDER_KEY,
    PIXEL_PIN_KEY,
    SUDO_PASSWORD_KEY
]


class NeopixelIlluminationPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.ShutdownPlugin,
    octoprint.plugin.RestartNeedingPlugin,
):
    def __init__(self):
        super().__init__()
        self._config: dict = {}
        self._current_brightness: float = None
        self._current_color: str = None
        self._pixels: neopixel.NeoPixel = None
        self._api_process: subprocess.Popen = None
        self._delegate: SocketNeoPixelDelegate = None

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            BRIGHTNESS_KEY: 1.0,
            ENABLED_KEY: False,
            NEOPIXEL_API_HOST_KEY: NEOPIXEL_API_SOCKET,
            NUM_PIXELS_KEY: 24,
            PIXEL_ORDER_KEY: neopixel.GRBW,
            PIXEL_PIN_KEY: 18,
            STARTUP_COLOR_KEY: "#ffffff",
            PARSE_GCODE_KEY: False,
            SUDO_PASSWORD_KEY: SUDO_DEFAULT_PASSWORD
        }

    def get_settings_restricted_paths(self):
        return {
            "never": [[SUDO_PASSWORD_KEY]]
        }

    def get_settings_version(self):
        return 1

    def get_template_configs(self):
        return [
            {
                "type": "settings",
                "custom_bindings": False,
            },
            {
                "type": "tab",
                "custom_bindings": True,
            },
            {
                "type": "navbar",
                "custom_bindings": True,
            },
        ]

    def get_template_vars(self):
        return {"pixel_order_list": PIXEL_ORDER_LIST}

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": [
                "vendor/coloris/coloris.js",
                "js/neopixel_illumination.js",
                "js/coloris_cfg.js",
            ],
            "css": ["vendor/coloris/coloris.css", "css/neopixel_illumination.css"],
            "less": ["less/neopixel_illumination.less"],
        }

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "neopixel_illumination": {
                "displayName": "Neopixel Illumination Plugin",
                "displayVersion": self._plugin_version,
                # version check: github repository
                "type": "github_release",
                "user": "brettvitaz",
                "repo": "OctoPrint-Neopixel_Illumination",
                "current": self._plugin_version,
                # update method: pip
                "pip": "https://github.com/brettvitaz/OctoPrint-Neopixel_Illumination/archive/{target_version}.zip",
            }
        }

    def on_settings_initialized(self):
        self._config = {
            setting_name: self._settings.get([setting_name])
            for setting_name in CONFIG_ITEMS
        }

    def on_settings_save(self, data):
        diff = super().on_settings_save(data)
        self._initialize_pixel()

        return diff

    def on_after_startup(self):
        sudo_password = self._settings.get([SUDO_PASSWORD_KEY])
        self._initialize_api(sudo_password)
        self._initialize_pixel()

    def get_api_commands(self):
        return {
            UPDATE_COLOR_COMMAND: ["color"],
            SAVE_COLOR_COMMAND: [],
            UPDATE_BRIGHTNESS_COMMAND: ["value"],
            SAVE_BRIGHTNESS_COMMAND: [],
        }

    def on_api_command(self, command, data):
        if command == UPDATE_COLOR_COMMAND:
            self._current_color = data[COLOR_KEY]
            self._set_pixels(self._current_color)
        elif command == SAVE_COLOR_COMMAND:
            self._settings.set([STARTUP_COLOR_KEY], self._current_color)
            self._settings.save()
        elif command == UPDATE_BRIGHTNESS_COMMAND:
            self._current_brightness = float(data["value"])
            self._set_brightness(self._current_brightness)
        elif command == SAVE_BRIGHTNESS_COMMAND:
            self._settings.set([BRIGHTNESS_KEY], self._current_brightness)
            self._settings.save()

    def on_shutdown(self):
        if self._api_process is not None:
            try:
                passwd_process = subprocess.Popen(["echo", (self._settings.get([SUDO_PASSWORD_KEY]))], stdout=subprocess.PIPE)
                subprocess.Popen(["sudo", "-S", "kill", str(self._api_process.pid)], stdin=passwd_process.stdout)
                self._api_process.wait(10)
                self._logger.info("Shut down NeoPixel api.")
            except:
                self._logger.info("NeoPixel api does not exist.")

    def _initialize_api(self, sudo_password):
        if self._api_process is None:
            api_filename = os.path.join(self._basefolder, "sock_api.py")
            passwd_process = subprocess.Popen(["echo", sudo_password], stdout=subprocess.PIPE)
            self._api_process = subprocess.Popen(
                [
                    "sudo",
                    "-S",
                    sys.executable,
                    api_filename,
                    "-l",
                    self._settings.get_plugin_logfile_path(postfix="api")
                ], stdin=passwd_process.stdout)
            self._logger.info("Started NeoPixel api {} `{}`".format(self._api_process.pid, " ".join(self._api_process.args)))

    def _parse_color(self, hex_color: str):
        if hex_color.startswith("#"):
            rgbw = int(f"{hex_color[1:]:<08}", 16)
            red = (rgbw >> 24) & 0xFF
            green = (rgbw >> 16) & 0xFF
            blue = (rgbw >> 8) & 0xFF
            white = rgbw & 0xFF

            return red, green, blue, white

    def _set_brightness(self, value: float):
        if self._settings.get_boolean([ENABLED_KEY]):
            self._pixels.brightness = value
            self._pixels.show()

    def _set_pixels(self, hex_color: str):
        if self._settings.get_boolean([ENABLED_KEY]):
            self._pixels.fill(self._parse_color(hex_color))
            self._pixels.show()

    def _initialize_pixel(self):
        enabled = self._settings.get_boolean(["enabled"])
        if enabled:
            self._current_brightness = self._settings.get_float(["brightness"])
            num_pixels = self._settings.get_int(["num_pixels"])
            pixel_order = self._settings.get(["pixel_order"])
            pixel_pin = self._settings.get_int(["pixel_pin"])
            self._current_color = self._settings.get(["startup_color"])

            delegate = SocketNeoPixelDelegate(SOCKET_SERVER_ADDRESS, self._logger)

            self._pixels = neopixel.NeoPixel(
                Pin(pixel_pin),
                int(num_pixels),
                brightness=self._current_brightness,
                auto_write=False,
                pixel_order=pixel_order,
                delegate=delegate,
            )

            # demo(self._pixels)
            self._set_pixels(self._current_color)

    def process_gcode(self, comm, phase, cmd: str, cmd_type, gcode, subcode, tags):
        # M150 [B<intensity>] [I<pixel>] [P<intensity>] [R<intensity>] [S<strip>] [U<intensity>] [W<intensity>]
        # M150 B100 R255 U50 W0
        if (
            self._settings.get([ENABLED_KEY])
            and self._settings.get([PARSE_GCODE_KEY])
            and gcode.upper().startswith(SET_COLOR_GCODE)
        ):
            parameter_list = cmd.split(" ")[1:]
            is_color_change = False
            index, brightness = -1, -1
            red, green, blue, white = 0, 0, 0, 0

            for parameter in parameter_list:
                parameter_key = parameter[0].upper()
                parameter_value = int(parameter[1:])

                if parameter_key == "I":
                    index = parameter_value
                elif parameter_key == "S":
                    pass  # not supported
                elif parameter_key == "P":
                    brightness = parameter_value / 255.0
                elif parameter_key == "R":
                    red = parameter_value
                    is_color_change = True
                elif parameter_key == "U":
                    green = parameter_value
                    is_color_change = True
                elif parameter_key == "B":
                    blue = parameter_value
                    is_color_change = True
                elif parameter_key == "W":
                    white = parameter_value
                    is_color_change = True

            if index >= 0 and is_color_change:
                self._pixels[index] = (red, green, blue, white)
            elif is_color_change:
                self._pixels.fill((red, green, blue, white))

            if brightness >= 0:
                self._pixels.brightness = brightness

            return None,

        return


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Neopixel Illumination"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
__plugin_pythoncompat__ = ">=3,<4"  # only python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = NeopixelIlluminationPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.sending": __plugin_implementation__.process_gcode,
    }
