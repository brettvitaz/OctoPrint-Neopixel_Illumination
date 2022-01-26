/*
 * View model for OctoPrint-Neopixel_Illumination
 *
 * Author: brettvitaz
 * License: AGPLv3
 */
$(function () {
    function NeopixelIlluminationViewModel(parameters) {
        var self = this;

        self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[1];

        self.currentColor = ko.observable();
        self.currentBrightness = ko.observable();

        self.onBeforeBinding = function () {
            self.currentColor(self.settingsViewModel.settings.plugins.neopixel_illumination.startup_color());
            self.currentBrightness(self.settingsViewModel.settings.plugins.neopixel_illumination.brightness());
        }

        self.saveColor = function (picker, event) {
            OctoPrint.simpleApiCommand("neopixel_illumination", "save_color")
        }

        self.saveBrightness = function (picker, event) {
            OctoPrint.simpleApiCommand("neopixel_illumination", "save_brightness")
        }

        self.updateColor = function (picker, event) {
            let newColor = event.currentTarget.value;
            if (newColor) {
                self.currentColor(newColor);
                OctoPrint.simpleApiCommand("neopixel_illumination", "update_color", {"color": newColor});
            }
        }

        self.updateBrightness = function (picker, event) {
            let newBrightness = event.currentTarget.value;
            if (newBrightness) {
                self.currentBrightness(newBrightness);
                OctoPrint.simpleApiCommand("neopixel_illumination", "update_brightness", {"value": newBrightness});
            }
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: NeopixelIlluminationViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["loginStateViewModel", "settingsViewModel"],
        // Elements to bind to, e.g. #settings_plugin_neopixel_illumination, #tab_plugin_neopixel_illumination, ...
        elements: ["#navbar_plugin_neopixel_illumination", "#tab_plugin_neopixel_illumination"]
    });
});
