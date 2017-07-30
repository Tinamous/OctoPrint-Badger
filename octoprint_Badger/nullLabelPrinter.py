
# A dummy label printer just creates the label and leaves the pdf on disk
# for inspection/debugging.
class NullLabelPrinter():
	def __init__(self, logger, settings, data_folder, label):
		self._logger = logger
		self._settings = settings
		self._data_folder = data_folder
		self._label = label

	def initialize(self):
		self._logger.info("Initialize null label printer")

	def get_printers(self):
		return ["Dymo_LabelWriter_NullType", "Another_Dymo_LabelWriter_NullType"]

	def print_do_not_hack_label(self, user, remove_after):
		self._logger.warn("Null Label printer printing label...")
		filename = self._label.create_user_label(user, remove_after)
		self._logger.warn("Do Not Hack label saved to: {0}".format(filename))

	def print_text_label(self, text):
		filename = self._label.create_text_label(text)
		self._logger.warn("Text label saved to: {0}".format(filename))

	def print_how_to_register(self):
		self._logger.warn("Null Label printer printing how to register label...")
		filename = self._label.create_register_label()
		self._logger.warn("Register label saved to: {0}".format(filename))