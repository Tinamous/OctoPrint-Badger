from .label import shippingLabel, largeAddressLabel

# A dummy label printer
class nullLabelPrinter():
	def __init__(self, logger, settings, data_folder, label):
		self._logger = logger
		self._settings = settings
		self._data_folder = data_folder
		# Label type defined in settings.
		self._label = label

	def initialize(self):
		self._logger.info("Initialize null label printer")

	def get_printers(self):
		return ["Dymo_LabelWriter_NullTupe"]

	def print_label(self, user):
		self._logger.warn("Null Label printer printing label...")
		filename = self._label.create_user_label(user)
		self._logger.warn("User label saved to: {0}".format(filename))

	def print_how_to_register(self):
		self._logger.warn("Null Label printer printing how to register label...")
		import socket
		hostname = socket.gethostname()
		host = socket.gethostbyname(hostname)
		self._logger.warn("Null Label printer hostname: {0}, host: {1}".format(hostname, host))

		filename = self._label.create_register_label()
		self._logger.warn("Register label saved to: {0}".format(filename))