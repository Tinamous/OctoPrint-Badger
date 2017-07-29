
from .nullLabelPrinter import nullLabelPrinter
from .cupsLabelPrinter import cupsLabelPrinter
from .label import shippingLabel, largeAddressLabel

class labelPrinter():
	def __init__(self, logger, settings, data_folder):
		self._logger = logger
		self._settings = settings
		self._data_folder = data_folder;

	def initialize(self):
		# TODO: Figure out which label printer system to use.
		printer = self._settings.get(["printer"])
		label = self.get_label();


		if printer == "Null Printer":
			self._actualLabelPrinter = nullLabelPrinter(self._logger, self._settings, self._data_folder, label)
			self._actualLabelPrinter.initialize()
		else:
			self._actualLabelPrinter = cupsLabelPrinter(self._logger, self._settings, self._data_folder, label)
			self._actualLabelPrinter.initialize()

	def get_label(self):
		label_template = self._settings.get(["labelTemplate"])

		if label_template == "Shipping":
			return shippingLabel(self._logger, self._data_folder)
		else:
			return largeAddressLabel(self._logger, self._data_folder)


	def get_printers(self):
		return self._actualLabelPrinter.get_printers()

	def print_label(self, user):
		self._actualLabelPrinter.print_label(user)

	def print_how_to_register(self):
		self._actualLabelPrinter.print_how_to_register()
