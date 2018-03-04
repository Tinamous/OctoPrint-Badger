import logging

from octoprint_Badger.Labels.largeAddressLabel import LargeAddressLabel
from octoprint_Badger.Labels.largeAddressLabelV2 import LargeAddressLabelV2
from octoprint_Badger.Labels.shippingLabel import ShippingLabel
from .cupsLabelPrinter import CupsLabelPrinter
from .nullLabelPrinter import NullLabelPrinter

# Responsible for label printer and label selection
# and delegation of the label printing task to the
# appropriate label printer.
class LabelPrinter():
	def __init__(self):
		# Temp one until assigned through initialize
		# which may not be called when getting the printers.
		self._logger = logging.getLogger('LabelPrinter')

	# Called before initialize as used by on_settings_load
	def get_printers(self):
		try:
			# If CUPS was available then return the cups printers.
			cupsPrinter = CupsLabelPrinter();
			return cupsPrinter.get_printers()
		except:
			# If CUPS printing failed offer only the null printer.
			self._logger.warn("Cups printer failed. Returning Null Printer")
			return ["Null Printer"]

	def initialize(self, logger, settings, data_folder):
		self._logger = logger
		self._settings = settings
		self._data_folder = data_folder

		# TODO: Figure out which label printer system to use.
		printer = self._settings.get(["printer"])
		label = self.get_label();

		if printer == "Null Printer":
			self._actualLabelPrinter = NullLabelPrinter()
			self._actualLabelPrinter.initialize(self._logger, self._settings, self._data_folder, label)
		else:
			self._actualLabelPrinter = CupsLabelPrinter()
			self._actualLabelPrinter.initialize(self._logger, self._settings, self._data_folder, label)

		# TODO: Setup a timer to cancel old print jobs...

	def get_label(self):
		label_template = self._settings.get(["labelTemplate"])
		x_offset = int(self._settings.get(["xOffset"]))
		y_offset = int(self._settings.get(["yOffset"]))
		date_format = self._settings.get(["dateFormat"])

		# TODO: Replace this with a plugin version to look for SuperLabel sub classes.
		if label_template == "99014 - Shipping":
			return ShippingLabel(self._logger, self._data_folder, x_offset, y_offset, date_format)
		elif label_template == "99012 - Large Address - Alternative":
			return LargeAddressLabelV2(self._logger, self._data_folder, x_offset, y_offset, date_format)
		else:
			return LargeAddressLabel(self._logger, self._data_folder, x_offset, y_offset, date_format)

	# Print the Do Not Hack Label
	# User should be dict version of user object
	# remove after the date after which the item
	# should be removed from storage.
	def print_do_not_hack_label(self, user, remove_after, label_serial_number):
		job_id = self._actualLabelPrinter.print_do_not_hack_label(user, remove_after, label_serial_number)
		return job_id

	def print_member_box_label(self, user):
		job_id = self._actualLabelPrinter.print_member_box_label(user)
		return job_id

	# Print a generic text label
	def print_text_label(self, text):
		job_id = self._actualLabelPrinter.print_text_label(text)
		return job_id

	def print_name_badge_label(self, name, comment):
		job_id = self._actualLabelPrinter.print_name_badge_label(name, comment)
		return job_id

	def print_hack_me_label(self, label_serial_number):
		job_id = self._actualLabelPrinter.print_hack_me_label(label_serial_number)
		return job_id

	# Print how to register label for when the user has tagged the rfid sensor
	# but is not registered and so can't be found
	def print_how_to_register(self, fob_id):
		job_id = self._actualLabelPrinter.print_how_to_register(fob_id)
		return job_id

	def clear_print_queue(self):
		self._logger.warn("Clearing the print queue...")
		try:
			self._actualLabelPrinter.clear_print_queue()
		except Exception as e:
			self._logger.error("Error clearing the print queue: {0}".format(e))

	def get_print_queue(self):
		try:
			return self._actualLabelPrinter.get_print_queue()
		except Exception as e:
			self._logger.error("Error getting the print queue: {0}".format(e))
			return []

	def cancel_old_print_jobs(self):
		try:
			self._logger.warn("Cancelling old print jobs...")
			if not self._actualLabelPrinter == None:
				return self._actualLabelPrinter.cancel_old_print_jobs()
		except Exception as e:
			self._logger.error("Error cancelling old print jobs: {0}".format(e))

	def get_printer_info(self):
		return self._actualLabelPrinter.get_printer_info()
