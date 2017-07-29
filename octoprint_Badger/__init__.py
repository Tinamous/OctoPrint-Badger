# coding=utf-8
from __future__ import absolute_import

import flask
import logging
import logging.handlers
import time

import octoprint.plugin
from octoprint.events import eventManager, Events
from octoprint.util import RepeatedTimer

from .tagReader import tagReader
from .labelPrinter import labelPrinter
from .nullTagReader import nullTagReader

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
			rfidComPort="AUTO",
			canRegister=True,
			rfidReaderType="Null Tag Reader",
			readerOptions=["None", "Null Tag Reader", "Micro RWD HiTag2"],
			labelTemplate="Shipping",
			labelTemplates=["Shipping", "Large Address"],
			printer="Null Printer",
			printers=self._printers
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
			PrintLabel=["tagId"],
		)

	# API POST command
	def on_api_command(self, command, data):
		self._logger.info("On api POST Data: {}".format(data))

		if command == "PrintLabel":
			self._logger.info("Print Label Request: {}".format(data))
			#payload = dict(keyfobId=data["rfidTag"])
			# This should raise rfid tag seen the same as would be raised
			# by the rfid reader
			# and should use the logged in users tag.
			pluginData = dict(eventEvent="RfidTagSeen", eventPayload=data)
			self._event_bus.fire("RfidTagSeen", data)

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

		self._labeller = labelPrinter(self._logger, self._settings, data_folder)
		self._labeller.initialize();

	def print_label(self):
		self._logger.info("Printing label......")
		self._labeler.print_label()

	##~~ RFID Tag Handling
	def initialize_tag_reader(self):
		self._logger.info("Initialize RFID reader")
		self._reader = tagReader(self._logger, self._settings, self._event_bus)
		self._reader.initialize()

	##~~ General Implementation

	def handle_rfid_tag_seen_event(self, payload):
		tagId = payload["tagId"]
		self._logger.info("RFID Tag (Event) Seen: " + tagId)

		# Raise the plugin message for an RfidTagSeen.
		pluginData = dict(eventEvent="RfidTagSeen", eventPayload=payload)
		self._plugin_manager.send_plugin_message(self._identifier, pluginData)

		# Find the user this tag belongs to
		user = self.find_user_from_tag(tagId)

		filename = ""
		try:
			if (user == None):
				self._logger.info("Did not find a user for the tag, printing how to register tag.")
				filename = "HowToRegister"
				self.fire_print_started(filename)
				self._labeller.print_how_to_register()

				# Also publish the unknown RFID Tag.
				pluginData = dict(eventEvent="UnknownRfidTagSeen", eventPayload=payload)
				self._plugin_manager.send_plugin_message(self._identifier, pluginData)
			else:
				# User was found so handle a known user swipping the RFID
				username = user["name"]
				self._logger.info("Printing label for {0}.".format(username))
				filename = username

				self.fire_print_started(filename)
				data = dict(username=username)
				self._labeller.print_label(user)

			self.fire_print_done(filename)
		except Exception as e:
			self._logger.error("Failed to print label. Error: {0}".format(e))
			self.fire_print_failed(filename)


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

