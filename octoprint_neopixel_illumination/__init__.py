# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

try:
    import neopixel
    from microcontroller import Pin
except:
    from .mocks import neopixel
    from .mocks.microcontroller import Pin

    print("For development only...")

PIXEL_ORDERS = [
    neopixel.GRB,
    neopixel.GRBW,
    neopixel.RGB,
    neopixel.RGBW,
]


class NeopixelIlluminationPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
):
    def __init__(self):
        super().__init__()
        self._pixels = None

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            "brightness": 0.2,
            "enabled": False,
            "num_pixels": 24,
            "on_startup": False,
            "pixel_order": "GRBW",
            "pixel_pin": 10,
            "url": "https://en.wikipedia.org/wiki/Hello_world",
        }

    def get_settings_version(self):
        return 1

    def get_template_configs(self):
        return [
            {
                "type": "settings",
                "name": "Neopixel Illumination",
                "custom_bindings": False,
            },
        ]

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/neopixel_illumination.js"],
            "css": ["css/neopixel_illumination.css"],
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

    def on_after_startup(self):
        self._logger.info("Hello Neopixel")
        brightness = self._settings.get(["brightness"])
        enabled = self._settings.get(["enabled"])
        num_pixels = self._settings.get(["num_pixels"])
        on_startup = self._settings.get(["on_startup"])
        pixel_order = self._settings.get(["pixel_order"])
        pixel_pin = self._settings.get(["pixel_pin"])
        self._logger.info(f"{enabled}, {type(enabled)}")
        if enabled:
            self._logger.info(f"{brightness}, {type(brightness)}")
            self._logger.info(f"{num_pixels}, {type(num_pixels)}")
            self._logger.info(f"{on_startup}, {type(on_startup)}")
            self._logger.info(f"{pixel_order}, {type(pixel_order)}")
            self._logger.info(f"{pixel_pin}, {type(pixel_pin)}")
            self._pixels = neopixel.NeoPixel(
                Pin(pixel_pin),
                num_pixels,
                brightness=brightness,
                auto_write=False,
                pixel_order=pixel_order,
            )
            if on_startup:
                self._pixels.fill((255, 0, 0, 0))
                self._pixels.show()
            else:
                self._pixels.fill((0, 0, 0, 0))
                self._pixels.show()


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
# __plugin_name__ = "Neopixel Illumination Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
__plugin_pythoncompat__ = ">=3,<4"  # only python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = NeopixelIlluminationPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
