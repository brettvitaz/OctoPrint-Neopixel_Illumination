# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

import board
import neopixel

pixel_pin = board.D10
num_pixels = 24
pixel_order = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=pixel_order)


class NeopixelIlluminationPlugin(octoprint.plugin.SettingsPlugin,
                                 octoprint.plugin.AssetPlugin,
                                 octoprint.plugin.TemplatePlugin,
                                 octoprint.plugin.StartupPlugin
                                 ):

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            'pixel_pin': 10
        }

    def get_settings_version(self):
        return 1

    def get_template_configs(self):
        return [
            dict(type="settings", name="Neopixel Illumination", custom_bindings=False),
        ]

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/neopixel_illumination.js"],
            "css": ["css/neopixel_illumination.css"],
            "less": ["less/neopixel_illumination.less"]
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
        pixels.fill((0, 255, 255, 0))
        pixels.show()


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
#__plugin_name__ = "Neopixel Illumination Plugin"

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
