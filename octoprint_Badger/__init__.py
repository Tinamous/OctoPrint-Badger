# coding=utf-8
from __future__ import absolute_import

import datetime
import flask
import logging
import logging.handlers
import time

import octoprint.plugin
from octoprint.events import eventManager, Events
from octoprint.util import RepeatedTimer
from flask.ext.login import current_user

from .tagReader import TagReader
from .labelPrinter import LabelPrinter
from .nullTagReader import NullTagReader

class BadgerPlugin(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.ShutdownPlugin,
                   octoprint.plugin.SettingsPlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.SimpleApiPlugin,
                   octoprint.plugin.EventHandlerPlugin):

	def __init__(self):
		self._printers = ["Null Printer", "DYMO_LabelWriter_450", "Another Printer"]
		self._reader = None

	def initialize(self):
		self._logger.setLevel(logging.DEBUG)
		self._logger.info("Badger Plugin [%s] initialized..." % self._identifier)

	# Startup complete we can not get to the settings.
	def on_after_startup(self):
		self._logger.info("Badger Plugin on_after_startup")
		# Initialize printers
		self.initialize_printers()
		# Initialzie the rfid tag reader
		self.initialize_tag_reader()

	def on_shutdown(self):
		self._logger.info("Badger on_shutdown...")
		self._reader.on_shutdown()
		self._logger.info("Badger on_shutdown completed.")

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		# rfidReaderType="Micro RWD HiTag2",
		# printer="DYMO_LabelWriter_450",
		return dict(
			removeAfterMonths=3,
			rfidComPort="AUTO",
			canRegister=True,
			rfidReaderType="Null Tag Reader",
			readerOptions=["None", "Null Tag Reader", "Micro RWD HiTag2"],
			labelTemplate="99014 - Shipping",
			labelTemplates=["99014 - Shipping", "99012 - Large Address"],
			printer="Null Printer",
			printers=self._printers,
			# Text X Offset in mm (Labels typically have a min of 5mm left margin
			xOffset=6,
		)

	def on_settings_save(self, data):
		self._logger.info("on_settings_save")
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		# reinitialize the printers to handle possible changes
		self.initialize_printers()
		# Handle posisble port or RFID reader changed
		self.initialize_tag_reader()

	def get_template_configs(self):
		return [
			# dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=False),
			dict(type="tab", name="Badger")
		]

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/Badger.js"],
			css=["css/Badger.css"],
			less=["less/Badger.less"]
		)

	##~~ API

	def on_api_get(self, request):
		self._logger.info("on_api_get")
		return flask.jsonify(dict())

	# API POST command options
	def get_api_commands(self):
		self._logger.info("On api get commands")

		return dict(
			# Emulate a tag having been seen
			TagSeen=["tagId"],
			# Print Do Not Hack for the current logged in user
			PrintDoNotHack=[],
			# Print text
			PrintText=["text"],
		)

	# API POST command
	def on_api_command(self, command, data):
		self._logger.info("On api POST Data: {}".format(data))

		if command == "TagSeen":
			# Debugging helper to emulate the RFID event raised when a tag is seen.
			self._logger.error("TagSeen Request: {}".format(data))
			# This should raise rfid tag seen the same as would be raised
			# by the rfid reader
			pluginData = dict(eventEvent="RfidTagSeen", eventPayload=data)
			self._event_bus.fire("RfidTagSeen", data)
		elif command == "PrintDoNotHack":
			user = self.find_user_from_current_user()
			self.print_do_not_hack_label(user)
		elif command == "PrintText":
			self.print_text_label(data["text"])
		else:
			self._logger.error("Unknown command: {0}".format(command))


	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			Badger=dict(
				displayName="OctoPrint Badger Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="Tinamous",
				repo="OctoPrint-Badger",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/Tinamous/OctoPrint-Badger/archive/{target_version}.zip"
			)
		)

	##~~ User manageement

	def find_user_from_current_user(self):
		username = current_user.get_name()
		self._logger.info("Current User: {0}".format(username))
		user = self._user_manager.findUser(username)
		self._logger.info("User: {0}".format(user))
		# Unlike getAllUsers, findUser returns the actual user
		# not a dict, so convert to a dict so it matches
		# how we are handling the user.
		return user.asDict()

	def find_user_from_tag(self, tagId):
		self._logger.info("Getting user for tag {0}".format(tagId))

		users = self._user_manager.getAllUsers()
		for user in users:
			user_settings = user["settings"]
			user_key_fob = user_settings.get("keyfobId")
			if tagId == user_key_fob:
				return user

		self._logger.info("No user found for tag")
		return None

	##~~ OctoPrint Event Handling (EventHandler Plugin)

	# RFID reader raises events when a tag is seen
	# Reader may be part of a different plugin so this allows
	# us to handle it on both.
	def on_event(self, event, payload):
		# Event may come from us, or another source (e.g. Who's Printing plugin).
		if event == "RfidTagSeen":
			self.handle_rfid_tag_seen_event(payload)

	##~~ Printer handling

	def initialize_printers(self):
		self._logger.info("Initialize Labeller")
		data_folder = self.get_plugin_data_folder();
		self._logger.info("Badger folder: {0}".format(data_folder));

		self._labeller = LabelPrinter(self._logger, self._settings, data_folder)
		self._labeller.initialize();

	def print_do_not_hack_label(self, user):
		self._logger.info("Printing Do Not Hack Label")
		filename = user["name"]

		try:
			self._logger.info("Printing label for {0}.".format(filename))
			# Compute when the member should remove the item.
			# Set in plugin config. Maybe user dependant as well?
			removeAfterMonths = int(self._settings.get(["removeAfterMonths"]))
			removeAfter = datetime.date.today() + datetime.timedelta(removeAfterMonths*365/12)

			self.fire_print_started(filename)
			self._labeller.print_do_not_hack_label(user, removeAfter)
			self.fire_print_done(filename)
		except Exception as e:
			self._logger.error("Failed to print label. Error: {0}".format(e))
			self.fire_print_failed(filename)

	def print_text_label(self, text):
		try:
			self._logger.info("Printing text label......")
			self.fire_print_started("text")
			self._labeller.print_text_label(text)
			self.fire_print_done("text")
		except Exception as e:
			self._logger.error("Failed to print label. Error: {0}".format(e))
			self.fire_print_failed("text")

	def print_how_to_register(self):
		filename = "HowToRegister"
		try:
			self._logger.info("Did not find a user for the tag, printing how to register tag.")
			self.fire_print_started(filename)
			self._labeller.print_how_to_register()
			self.fire_print_done(filename)
		except Exception as e:
			self._logger.error("Failed to print label. Error: {0}".format(e))
			self.fire_print_failed(filename)

	##~~ RFID Tag Handling
	def initialize_tag_reader(self):
		self._logger.info("Initialize RFID reader")
		self._reader = TagReader(self._logger, self._settings, self._event_bus)
		self._reader.initialize()

	def handle_rfid_tag_seen_event(self, payload):
		tagId = payload["tagId"]
		self._logger.info("RFID Tag (Event) Seen: " + tagId)

		# Raise the plugin message for an RfidTagSeen.
		pluginData = dict(eventEvent="RfidTagSeen", eventPayload=payload)
		self._plugin_manager.send_plugin_message(self._identifier, pluginData)

		# Find the user this tag belongs to
		user = self.find_user_from_tag(tagId)

		if (user == None):
			self.print_how_to_register()
		else:
			self.print_do_not_hack_label(user)

	##~~ General Implementation

	def fire_print_started(self, filename):
		data_folder = self.get_plugin_data_folder();
		payload = dict(name=filename, path=data_folder, origin="local", file=filename + ".gcode")
		self._event_bus.fire(Events.PRINT_STARTED, payload);

	def fire_print_done(self, filename):
		data_folder = self.get_plugin_data_folder();
		payload = dict(name=filename, path=data_folder, origin="local", file=filename + ".gcode", time= time.time())
		self._event_bus.fire(Events.PRINT_DONE, payload);

	def fire_print_failed(self, filename):
		data_folder = self.get_plugin_data_folder();
		payload = dict(name=filename, path=data_folder, origin="local", file= filename + ".gcode")
		self._event_bus.fire(Events.PRINT_FAILED, payload)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Badger"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = BadgerPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

