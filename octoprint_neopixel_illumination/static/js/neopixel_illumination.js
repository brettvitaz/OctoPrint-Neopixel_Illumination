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

        // TODO: Implement your plugin's view model here.

        self.currentColor = ko.observable();
        self.newColor = ko.observable()

        // this will be called when the user clicks the "Go" button and set the iframe's URL to
        // the entered URL
        self.goToUrl = function () {
            self.currentColor(self.newColor());
        };

        // This will get called before the HelloWorldViewModel gets bound to the DOM, but after its
        // dependencies have already been initialized. It is especially guaranteed that this method
        // gets called _after_ the settings have been retrieved from the OctoPrint backend and thus
        // the SettingsViewModel been properly populated.
        self.onBeforeBinding = function () {
            self.newColor(self.settingsViewModel.settings.plugins.neopixel_illumination.startup_color());
            self.goToUrl();
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
        elements: ["#tab_plugin_neopixel_illumination"]
    });
});
