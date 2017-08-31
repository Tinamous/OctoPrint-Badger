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

        self.status = ko.observable("");
        self.printerInfo = ko.observable();
        self.textBlock = ko.observable("");

        self.notLoggedIn = ko.computed(function() {
            return !self.loginStateViewModel.isUser();
        });

        self.onBeforeBinding = function () {
            self.settings = self.settingsViewModel.settings.plugins.badger;
        };

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "badger") {
                return;
            }

            switch (data.eventEvent) {

                // Any tag seen. This can probably be ignored
                // as only Unknown Rfid Tags should be used for registration.
                case "RfidTagSeen":
                    console.log("Badger: User tag seen. TagId:" + data.eventPayload.tagId);
                    return;
                // If the tag was seen and it is unknown.
                case "UnknownRfidTagSeen":
                    console.log("Badger: Unknown tag seen. TagId:" + data.eventPayload.tagId);
                    // If in normal mode, show a "Unknown Tag, please register" message
                    // If not logged in it won't be visible anyway
                    //self.unknownTagSeen(true);
                    // This needs to be cleared if the tag was used for registering.
                    return;
                // If the tag was seen and it is unknown.
                case data.eventEvent == "PrintDone":
                    console.log("Print Done data: " + data);
                    self.status("");

                    var text = "<div>";
                    text += "<ul class='icons-ul'>";
                    text += "<li><span>Label Type: " + data.label_type + "</span></li>";
                    text += "<li><span>Job Id: " + data.job_id + "</span></li>";
                    text += "<li><span>Details: " + data.filename + "</span></li>";
                    text += "</div>";

                    var options = {
                            title: "Label Printed",
                            text: text, //"Label printed: Label: " + data.label_type + ", Job Id: " + data.job_id + ", Details: " + data.filename,
                            hide: false,
                            type: "success"
                        };
                    self._showpopup(options, {});
                    break;
                case "PrintFailed":
                    console.log("Print Failed data: " + data);
                    self.status("");
                    var options = {
                        title: "Label Print Error",
                        text: "An error occurred printing the label.",
                        type: "error"
                    };
                    self._showpopup(options, {});
                    break;
            }
        };

        self.onUserLoggedIn = function(user) {
            self.getPrintQueue();
        };

        self.tagSeen = function() {
            console.log("Requesting print Do Not Hack Label");
            self.status("Printing...");
            var payload = { tagId:'12345678' };
            OctoPrint.simpleApiCommand(self.pluginId, "TagSeen", payload, {});
        };

        self.printDoNotHack = function() {
            console.log("Requesting print Do Not Hack label")
            self.status("Printing...");
            OctoPrint.simpleApiCommand(self.pluginId, "PrintDoNotHack", {}, {});
        };

        self.printMembersBox = function() {
            console.log("Requesting print members box label")
            self.status("Printing...");
            OctoPrint.simpleApiCommand(self.pluginId, "PrintMembersBox", {}, {});
        };

        self.printHowToRegister = function() {
            console.log("Requesting print How To Register Label");
            self.status("Printing...");
            OctoPrint.simpleApiCommand(self.pluginId, "PrintHowToRegister", {}, {});
        };

        self.printTextBlock = function() {
            console.log("Requesting print Do Not Hack Label");
            self.status("Printing...");
            var payload = { text:self.textBlock() };
            OctoPrint.simpleApiCommand(self.pluginId, "PrintText", payload, {});
        };

        self.printJobs = ko.observableArray([]);

        self.getPrintQueue = function() {
            self.printJobs([{jobId:"Loading", name:"Loading..."}]);
            OctoPrint.simpleApiGet(self.pluginId, {request:"getPrintQueue"})
                .done(function(response) {
                    console.log("Get Print Queue Response: " + response);
                    // do something with the response
                    var mappedJobs = $.map(response.jobs, function(job){
                        return {jobId:job.jobId, name:"job " + job.jobId};
                    });

                    console.log("Printer info: " + response.printerInfo);
                    self.printerInfo(response.printerInfo);

                    self.printJobs(mappedJobs)
                });
        };

        self.clearPrintQueue = function() {
            console.log("Requesting clear print queue")
            //self.status("Clearing Print Queue...");
            OctoPrint.simpleApiCommand(self.pluginId, "ClearPrintQueue", {}, {})
                .done(function() {
                    self.getPrintQueue();
                })
        };

        self.labelsRefilled = function() {
            console.log("Setting labels refilled")
            OctoPrint.simpleApiCommand(self.pluginId, "LabelsRefilled", {}, {});
        }

        self._showpopup = function(options, eventListeners) {
            self._closePopup();
            self.popup = new PNotify(options);

            if (eventListeners) {
                var popupObj = self.popup.get();
                _.each(eventListeners, function(value, key) {
                    popupObj.on(key, value);
                })
            }
        };

        self._closePopup = function() {
            if (self.popup !== undefined) {
                self.popup.remove();
            }
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
