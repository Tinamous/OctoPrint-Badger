# coding=utf-8
from __future__ import absolute_import

import datetime
import flask
import logging
import logging.handlers
import time
import sys
import sqlite3

import octoprint.plugin
from octoprint.events import eventManager, Events
from octoprint.util import RepeatedTimer
from flask.ext.login import current_user

from .tagReader import TagReader
from .labelPrinter import LabelPrinter
from .nullTagReader import NullTagReader

from .mockGPIO import MockGPIO
from .piGPIO import PiGPIO

from .dataAaccess import DataAccess

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
		self._gpio = None
		# TODO: Initialize these from database.
		self._labels_printed_this_roll = 0
		self._labels_low_warn_at = 250
		self._total_labels_printed_count = 0

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
		# Initialze GPIO handling
		self.initialize_gpio()
		# Initialize the database
		self.initialize_data_access()

	def on_shutdown(self):
		self._logger.info("Badger on_shutdown...")
		self._reader.on_shutdown()
		self._gpio.set_left_button_led(0)
		self._gpio.set_right_button_led(0)
		self._gpio.set_alive_led(0)
		self._logger.info("Badger on_shutdown completed.")

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		# rfidReaderType="Micro RWD HiTag2",
		# printer="DYMO_LabelWriter_450",
		return dict(
			removeAfterMonths=3,
			labelSerialNumberPrefix="T",
			dateFormat="%Y-%m-%d",
			rfidComPort="AUTO",
			canRegister=True,
			rfidReaderType="Null Tag Reader",
			readerOptions=["None", "Null Tag Reader", "Micro RWD HiTag2"],
			labelTemplate="99012 - Large Address",
			labelTemplates=["99012 - Large Address","99012 - Large Address - Alternative", "99014 - Shipping"],
			noButtonOption="DoNotHack",
			leftButtonOption="NameBadge",
			rightButtonOption="MembersBox",
			buttonOptions=["DoNotHack","NameBadge","MembersBox","HackMe"],
			bothButtonsOption="HackMe",
			bothButtonsOptions=["HackMe","LabelsReplaced"],
			printer="Null Printer",
			# Text X Offset in mm (Labels typically have a min of 5mm left margin
			xOffset=6,
			yOffset=0,
			# If this tag is seen then it indicated that the label roll has been replaced.
			labelsReplacedTagId="c01dbeef",
			# TODO: Change the event we use when swipped
			# the "RfidTagSeen" is also raised by the Who's Printing
			# Plugin. If we handled that as well we could print a
			# label for who's printing. (Or handle the Who's Printing)
			# event...
			handleRfidTagSeenEvent=True,
			printLabelForWhosPrinting=False,
		)

	# TODO: override on_settings_load and inject the list of printers.
	def on_settings_load(self):
		data = octoprint.plugin.SettingsPlugin.on_settings_load(self)
		data["printers"] = ["foo", "bar", "baz"]

		# We know the selected printing system at this time, so we couc
		# use that to get the printers
		try:
			labeller = LabelPrinter()
			data["printers"] = labeller.get_printers()
		except Exception as e:
			self._logger.error("Failed to get printers")
			data["printers"] = ["None"]

		return data

	def on_settings_save(self, data):
		self._logger.info("Badger saving settings...")
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		try:
			# reinitialize the printers to handle possible changes
			self.initialize_printers()
			# Handle posisble port or RFID reader changed
			self.initialize_tag_reader()
		except Exception as e:
			self._loger.error("Failed to initialize after settings change")

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

		try:
			# TODO: handle more than just the one get request option.
			jobs = self._labeller.get_print_queue()
			jobs_list = []
			for job in jobs:
				jobs_list.append(dict(jobId=job, jobUri=jobs[job]["job-uri"]))
				#TODO: Add the attributes

			# Get information on the currently selected printer.
			# a dict of printer information
			priter_info = self._labeller.get_printer_info()

			return flask.jsonify(dict(jobs=jobs_list, printerInfo=priter_info))
		except Exception as e:
			self._logger.error("Error returning jobs. {0}".format(e))
			raise

	# API POST command options
	def get_api_commands(self):
		self._logger.info("On api get commands")

		return dict(
			# Emulate a tag having been seen
			TagSeen=["tagId"],
			# Print Do Not Hack for the current logged in user
			PrintDoNotHack=[],
			# Print label for members bos
			PrintMembersBox=[],
			# Print a traditional name badge
			PrintNameBadge=[],
			# Print a "Hack Me" label
			PrintHackMe=[],
			# Print text
			PrintText=["text"],
			# Print the how to register label
			PrintHowToRegister=[],
			# Clear the print queue of labels that
			# have not printed (i.e. when run out of labels)
			ClearPrintQueue=[],
			# Indicate that the labels have been replaced
			# reset the print counter.
			LabelsRefilled=[],
			# Update name badge Badger setting
			UpdateNameBadge=["badgerName","badgerComment"]
		)

	# API POST command
	def on_api_command(self, command, data):
		self._logger.info("On api POST Data: {}".format(data))
		user = self.find_user_from_current_user()

		if command == "TagSeen":
			# Debugging helper to emulate the RFID event raised when a tag is seen.
			self._logger.error("TagSeen Request: {}".format(data))
			# This should raise rfid tag seen the same as would be raised
			# by the rfid reader
			pluginData = dict(eventEvent="RfidTagSeen", eventPayload=data)
			self._event_bus.fire("RfidTagSeen", data)
		elif command == "PrintDoNotHack":
			self.print_do_not_hack_label(user)
		elif command == "PrintMembersBox":
			self.print_members_box_label(user)
		elif command == "PrintNameBadge":
			self.print_members_name_badge(user)
		elif command == "PrintHackMe":
			self.print_hack_me_label(user)
		elif command == "PrintText":
			self.print_text_label(user, data["text"])
		elif command == "PrintHowToRegister":
			self.print_how_to_register("c01dbeef")
		elif command=="ClearPrintQueue":
			self._labeller.clear_print_queue()
		elif command=="LabelsRefilled":
			self.labels_refilled()
		elif command=="UpdateNameBadge":
			self._logger.error("Update Name Badge not implemented yet: {0}".format(command))
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
		elif event == "BothButtonsPressed":
			self.handle_both_buttons_ressed(payload)


	##~~ Data Access

	def initialize_data_access(self):
		self._logger.info("Initialize Data Access")
		data_folder = self.get_plugin_data_folder();
		self._database = DataAccess(self._logger, self._settings, data_folder)
		self._logger.info("Done init. Data Access")

	##~~ Printer handling

	def initialize_printers(self):
		self._logger.info("Initialize Labeller")
		data_folder = self.get_plugin_data_folder();
		self._logger.info("Badger folder: {0}".format(data_folder));

		self._labeller = LabelPrinter()
		self._labeller.initialize(self._logger, self._settings, data_folder);

	def print_do_not_hack_label(self, user):
		self._logger.info("Printing Do Not Hack Label")
		filename = user["name"]
		label_type = "Do Not Hack"

		try:
			self._logger.info("Printing label for {0}.".format(filename))
			# Compute when the member should remove the item.
			# Set in plugin config. Maybe user dependant as well?
			removeAfterMonths = int(self._settings.get(["removeAfterMonths"]))
			removeAfter = datetime.date.today() + datetime.timedelta(removeAfterMonths*365/12)

			# Stores the label details and returns the serial number generated
			label_serial_number = self.get_label_serial_number(user, removeAfter);

			self.fire_print_started(filename)
			job_id = self._labeller.print_do_not_hack_label(user, removeAfter, label_serial_number)
			self.log_label_printed(job_id, label_type, label_serial_number, user, removeAfter);
			self.fire_print_done(filename, job_id, label_type, 1, label_serial_number, removeAfter)
		except Exception as e:
			self._logger.error("Failed to print do not hack label. Error: {0}".format(e))
			self.fire_print_failed(filename, label_type)

	def print_members_box_label(self, user):
		self._logger.info("Printing Members Box Label")
		filename = user["name"]
		label_type = "Members Box"

		try:
			self._logger.info("Printing box label for {0}.".format(filename))

			self.fire_print_started(filename)
			job_id = self._labeller.print_member_box_label(user)
			self.log_label_printed(job_id, label_type, filename, user);
			self.fire_print_done(filename, job_id, label_type)
		except Exception as e:
			self._logger.error("Failed to print members box label. Error: {0}".format(e))
			self.fire_print_failed(filename, label_type)

	def print_members_name_badge(self, user):
		self._logger.info("Print name badge. ")
		label_type = "Name Badge"

		user_settings = user["settings"]
		displayName = user_settings.get("displayName")
		badgerName = user_settings.get("badgerName")
		badgerComment = user_settings.get("badgerComment")

		if not badgerName:
			self._logger.error("no badger name specified, using display name")
			# for now, use the users setting until they have set their badger name.
			badgerName = displayName

		if not badgerComment:
			badgerComment = "Show me how to configure the badger"

		try:
			self._logger.info("Printing name badge label......")
			self.fire_print_started("name badge")
			job_id = self._labeller.print_name_badge_label(badgerName, badgerComment)
			self.log_label_printed(job_id, label_type, badgerName, user)
			self.fire_print_done("name badge", job_id, label_type)
		except Exception as e:
			self._logger.error("Failed to print name badge label. Error: {0}".format(e))
			self.fire_print_failed("name badge", label_type)

	def print_hack_me_label(self, user=None):
		self._logger.info("Printing hack me label.")
		label_type = "Hack Me"

		try:
			# Compute when the member should remove the item.
			# Set in plugin config. Maybe user dependant as well?
			remove_after_months = int(self._settings.get(["removeAfterMonths"]))
			remove_after = datetime.date.today() + datetime.timedelta(remove_after_months  * 365 / 12)

			# Stores the label details and returns the serial number generated
			label_serial_number = self.get_label_serial_number(user, remove_after);

			self.fire_print_started("hack me")
			job_id = self._labeller.print_hack_me_label(label_serial_number, remove_after)
			self.log_label_printed(job_id, label_type, label_serial_number, user, remove_after);
			self.fire_print_done("hack me", job_id, label_type, 1, label_serial_number, remove_after)
		except Exception as e:
			self._logger.error("Failed to print hack me label. Error: {0}".format(e))
			self.fire_print_failed("hack me", label_type)

	def print_text_label(self, user, text):
		label_type = "Text Label"
		try:
			self._logger.info("Printing text label......")
			self.fire_print_started("text")
			job_id = self._labeller.print_text_label(text)
			self.log_label_printed(job_id, label_type, text, user)
			self.fire_print_done("text", job_id, label_type)
		except Exception as e:
			self._logger.error("Failed to print text label. Error: {0}".format(e))
			self.fire_print_failed("text", label_type)

	def print_how_to_register(self, fob_id):
		filename = "HowToRegister"
		label_type = "How To Register"
		try:
			self._logger.info("Did not find a user for the tag, printing how to register tag.")
			self.fire_print_started(filename)
			job_id = self._labeller.print_how_to_register(fob_id)
			self.log_label_printed(job_id, label_type, "")
			self.fire_print_done(filename, job_id, label_type)
		except Exception as e:
			self._logger.error("Failed to print how to register label. Error: {0}".format(e))
			self.fire_print_failed(filename, label_type)

	def labels_refilled(self):
		self._logger.info("Labels refilled. ")
		self._labels_printed_this_roll = 0
		# TODO: Update the database.

	def check_labels_remaining(self):
		self._logger.info("TODO: Check labels remaining on roll")
		## 99012 has 260 labels on a roll.
		if self._labels_printed_this_roll > self._labels_low_warn_at:
			self._logger.warn("Running low on labels. Tell somebody....")

	##~~ RFID Tag Handling

	def initialize_tag_reader(self):
		self._logger.info("Initialize RFID reader")
		self._reader = TagReader(self._logger, self._settings, self._event_bus)
		self._reader.initialize()

	def handle_rfid_tag_seen_event(self, payload):
		tag_id = payload["tagId"]
		self._logger.info("RFID Tag (Event) Seen: " + tag_id)

		# set the LEDs flashing to show we are processing the tag
		self._gpio.set_left_button_led(0)
		self._gpio.set_right_button_led(0)

		# Raise the plugin message for an RfidTagSeen.
		pluginData = dict(eventEvent="RfidTagSeen", eventPayload=payload)
		self._plugin_manager.send_plugin_message(self._identifier, pluginData)

		labels_replaced_tag_id = self._settings.get(["labelsReplacedTagId"])
		if tag_id == labels_replaced_tag_id:
			self._logger.info("RFID Tag matches labels replaced tag. No further action needed...")
			self.labels_refilled()
			return

		# Find the user this tag belongs to
		user = self.find_user_from_tag(tag_id)

		if (user == None):
			self.print_how_to_register(tag_id)
		else:
			label_type = self.get_label_type_selected()

			if label_type == "DoNotHack":
				self.print_do_not_hack_label(user)
			elif label_type == "NameBadge":
				self.print_members_name_badge(user)
			elif label_type == "MembersBox":
				self.print_members_box_label(user)
			elif label_type == "HackMe":
				self.print_hack_me_label(user)
			else:
				# Fall back to DoNotHack for an unknown label type...
				self.print_do_not_hack_label(user)

		# restore LEDs to on state
		self._gpio.set_left_button_led(1)
		self._gpio.set_right_button_led(1)

	# Determine what button is pressed and return the label
	# type defined for that button.
	def get_label_type_selected(self):

		# No option for both buttons pressed as that needs 3 hands
		# Both button pressed is reserved to indicate the labels have
		# been replaced.

		if self._gpio.is_left_button_pressed():
			return self._settings.get(["leftButtonOption"])
		if self._gpio.is_right_button_pressed():
			return self._settings.get(["rightButtonOption"])

		return self._settings.get(["noButtonOption"])


	##~~ GPIO handling

	def initialize_gpio(self):


		# If we are actually on a Pi then replace the mock
		# with the real GPIO class.
		if sys.platform == "linux2":
			self._gpio = PiGPIO(self._logger, self._settings, self._event_bus)
		else:
			self._gpio = MockGPIO(self._logger, self._settings, self._event_bus)

		# Initialize the GPIO ports for switch/leds.
		self._logger.info("Init GPIO")
		self._gpio.initialize()

	def handle_both_buttons_ressed(self, payload):
		action = self._settings.get(["bothButtonsOption"])
		# bothButtonsOptions = ["HackMe", "LabelsReplaced"],
		if action == "HackMe":
			self.print_hack_me_label(None)
		elif action == "LabelsReplaced":
			self.labels_refilled()
		else:
			self._logger.error("Unknown action for both buttons pressed")

	##~~ General Implementation

	def log_label_printed(self, job_id, label_type, details, user = None, remove_after = None):
		# TODO: Store in database...
		# Do Not Hack will be stored with the remove_after
		self._logger.info("Label Printed. Type: {0}, details: {1}".format(label_type, details))
        # TODO: Decrement the number of labels left on the roll.

	# Set a serial number for the item stored (i.e. from the databsae.
	# user mignt be null if printing a HACK ME item.
	def get_label_serial_number(self, user, remove_after):
		label_number = self._database.get_serial_number()
		self._logger.info("Got label number: {0}".format(label_number))
		label_number_prefix = self._settings.get(["labelSerialNumberPrefix"])
		serial_number = "{0}-{1}".format(label_number_prefix, label_number)

		user_name = ""
		if user:
			user_name = user["name"]

		self._database.store_item(serial_number, user_name, remove_after)

		return serial_number

	##~~ Notifications
	def fire_print_started(self, filename):
		data_folder = self.get_plugin_data_folder();
		payload = dict(name=filename, path=data_folder, origin="local", file=filename + ".gcode")
		self._event_bus.fire(Events.PRINT_STARTED, payload);

	def fire_print_done(self, filename, job_id, label_type, number_of_labels = 1, serial_number = "", remove_after=""):
		data_folder = self.get_plugin_data_folder();
		self._labels_printed_this_roll = self._labels_printed_this_roll + number_of_labels
		self._total_labels_printed_count = self._total_labels_printed_count + number_of_labels

		payload = dict(name=filename,
		               path=data_folder,
		               origin="local",
		               file=filename + ".gcode",
		               time= time.time(),
		               label_type=label_type,
		               number_of_labels_printed=number_of_labels,
		               labels_printed_this_roll = self._labels_printed_this_roll,
		               total_labels_printed=self._total_labels_printed_count,
		               serial_number=serial_number,
		               remove_after=remove_after)
		self._event_bus.fire(Events.PRINT_DONE, payload);

		# Custom event
		self._event_bus.fire("LabelPrintDone", payload);

		# And notify the web clients
		payload = dict(eventEvent="PrintDone",message="Label Printed", filename=filename, job_id=job_id, label_type=label_type)
		self._plugin_manager.send_plugin_message(self._identifier, payload)

		self.check_labels_remaining()

	def fire_print_failed(self, filename, label_type):
		data_folder = self.get_plugin_data_folder();
		payload = dict(name=filename, path=data_folder, origin="local", file= filename + ".gcode")
		self._event_bus.fire(Events.PRINT_FAILED, payload)
		payload = dict(eventEvent="PrintFailed", message="Error printing label", label_type=label_type)
		self._plugin_manager.send_plugin_message(self._identifier, payload)
		self.check_labels_remaining()


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

