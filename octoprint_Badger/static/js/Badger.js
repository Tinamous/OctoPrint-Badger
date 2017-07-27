/*
 * View model for OctoPrint-Badger
 *
 * Author: Tinamous
 * License: AGPLv3
 */
$(function() {
    function BadgerViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        BadgerViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ /* "loginStateViewModel", "settingsViewModel" */ ],

        // e.g. #settings_plugin_Badger, #tab_plugin_Badger, ...
        [ /* ... */ ]
    ]);
});
