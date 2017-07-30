
from .nullLabelPrinter import NullLabelPrinter
from .cupsLabelPrinter import CupsLabelPrinter
from .shippingLabel import ShippingLabel
from .largeAddressLabel import LargeAddressLabel

# Responsible for label printer and label selection
# and delegation of the label printing task to the
# appropriate label printer.
class LabelPrinter():
	def __init__(self, logger, settings, data_folder):
		self._logger = logger
		self._settings = settings
		self._data_folder = data_folder

	def initialize(self):
		# TODO: Figure out which label printer system to use.
		printer = self._settings.get(["printer"])
		label = self.get_label();

		if printer == "Null Printer":
			self._actualLabelPrinter = NullLabelPrinter(self._logger, self._settings, self._data_folder, label)
			self._actualLabelPrinter.initialize()
		else:
			self._actualLabelPrinter = CupsLabelPrinter(self._logger, self._settings, self._data_folder, label)
			self._actualLabelPrinter.initialize()

		# TODO: Setup a timer to cancel old print jobs...

	def get_label(self):
		label_template = self._settings.get(["labelTemplate"])
		x_offset = int(self._settings.get(["xOffset"]))
		y_offset = int(self._settings.get(["yOffset"]))
		date_format = self._settings.get(["dateFormat"])

		if label_template == "99014 - Shipping":
			return ShippingLabel(self._logger, self._data_folder, x_offset, y_offset, date_format)
		else:
			return LargeAddressLabel(self._logger, self._data_folder, x_offset, y_offset, date_format)

	def get_printers(self):
		return self._actualLabelPrinter.get_printers()

	# Print the Do Not Hack Label
	# User should be dict version of user object
	# remove after the date after which the item
	# should be removed from storage.
	def print_do_not_hack_label(self, user, remove_after, label_serial_number):
		self._actualLabelPrinter.print_do_not_hack_label(user, remove_after, label_serial_number)

	def print_member_box_label(self, user):
		self._actualLabelPrinter.print_member_box_label(user)

	# Print a generic text label
	def print_text_label(self, text):
		self._actualLabelPrinter.print_text_label(text)

	# Print how to register label for when the user has tagged the rfid sensor
	# but is not registered and so can't be found
	def print_how_to_register(self, fob_id):
		self._actualLabelPrinter.print_how_to_register(fob_id)

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
