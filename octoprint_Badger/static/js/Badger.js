/*
 * View model for OctoPrint-Badger
 *
 * Author: Tinamous
 * License: AGPLv3
 */
$(function() {

    function BadgerViewModel(parameters) {
        var self = this;

        self.pluginId = "badger";

        self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[1];
        self.printer = parameters[2];

        self.notLoggedIn = ko.computed(function() {
            return !self.loginStateViewModel.isUser();
        })

        self.onBeforeBinding = function () {
            self.settings = self.settingsViewModel.settings.plugins.badger;
        };

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "badger") {
                return;
            }

            // Any tag seen. This can probably be ignored
            // as only Unknown Rfid Tags should be used for registration.
            if (data.eventEvent == "RfidTagSeen") {
                console.log("Badger: User tag seen. TagId:" + data.eventPayload.tagId);
            }

            // If the tag was seen and it is unknown.
            if (data.eventEvent == "UnknownRfidTagSeen") {
                console.log("Badger: Unknown tag seen. TagId:" + data.eventPayload.tagId);
                // If in normal mode, show a "Unknown Tag, please register" message
                // If not logged in it won't be visible anyway
                //self.unknownTagSeen(true);
                // This needs to be cleared if the tag was used for registering.
            }
        };

        self.onUserLoggedIn = function(user) {
            //self.populateUsers();
            //self.getWhosPrinting();
        };

        self.printLabel = function() {
            console.log("Requesting print label")
            var payload = { tagId:'12345678' };
            OctoPrint.simpleApiCommand(self.pluginId, "PrintLabel", payload, {});
        };
    }

    // view model class, parameters for constructor, container to bind to
    // New style config .
    OCTOPRINT_VIEWMODELS.push({
        construct: BadgerViewModel,
        additionalNames: [],
        dependencies: ["loginStateViewModel", "settingsViewModel", "printerStateViewModel"],
        optional: [],
        elements: ["#navbar_plugin_badger", "#tab_plugin_badger"]
    });
});
