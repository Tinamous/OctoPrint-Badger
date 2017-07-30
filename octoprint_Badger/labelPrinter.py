
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

	def get_label(self):
		label_template = self._settings.get(["labelTemplate"])
		xOffset = self._settings.get(["xOffset"])

		if label_template == "99014 - Shipping":
			return ShippingLabel(self._logger, self._data_folder, xOffset)
		else:
			return LargeAddressLabel(self._logger, self._data_folder, xOffset)

	def get_printers(self):
		return self._actualLabelPrinter.get_printers()

	# Print the Do Not Hack Label
	# User should be dict version of user object
	# remove after the date after which the item
	# should be removed from storage.
	def print_do_not_hack_label(self, user, remove_after):
		self._actualLabelPrinter.print_do_not_hack_label(user, remove_after)

	# Print a generic text label
	def print_text_label(self, text):
		self._actualLabelPrinter.print_text_label(text)

	# Print
	def print_how_to_register(self):
		self._actualLabelPrinter.print_how_to_register()
