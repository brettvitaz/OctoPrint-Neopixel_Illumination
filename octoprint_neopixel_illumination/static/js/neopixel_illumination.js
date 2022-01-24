/*
 * View model for OctoPrint-Neopixel_Illumination
 *
 * Author: brettvitaz
 * License: AGPLv3
 */
$(function () {
    function NeopixelIlluminationViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[1];

        self.currentColor = ko.observable();
        self.newColor = ko.observable()

        self.onBeforeBinding = function () {
            self.currentColor(self.settingsViewModel.settings.plugins.neopixel_illumination.startup_color());
        }

        self.saveColor = function (picker, event) {
            let newColor = event.currentTarget.value;
            if (newColor) {
                self.currentColor(newColor)
                OctoPrint.simpleApiCommand("neopixel_illumination", "update_color", {"color": newColor});
                OctoPrint.settings.savePluginSettings("neopixel_illumination", {"startup_color": newColor});
            }
        }

        self.updateColor = function (picker, event) {
            let newColor = event.currentTarget.value
            if (newColor) {
                self.currentColor(newColor)
                OctoPrint.simpleApiCommand("neopixel_illumination", "update_color", {"color": newColor});
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
