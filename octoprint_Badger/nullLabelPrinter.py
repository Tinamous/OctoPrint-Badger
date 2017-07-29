
# A dummy label printer
class nullLabelPrinter():
	def __init__(self, logger, settings):
		self._logger = logger
		self._settings = settings

	def initialize(self):
		self._logger.info("Initialize null label printer")

	def get_printers(self):
		return ["Dymo_LabelWriter_NullTupe"]

	def print_label(self, user):
		self._logger.warn("Null Label printer printing label...")
		self._logger.warn("User: {0}".format(user["name"]))
		user_settings = user["settings"]
		user_key_fob = user_settings.get("keyfobId")
		self._logger.warn("KeyFob: {0}".format(user["name"]))

	def print_how_to_register(self):
		self._logger.warn("Null Label printer printing how to register label...")
		import socket
		hostname = socket.gethostname()
		host = socket.gethostbyname(hostname)
		self._logger.warn("Null Label printer hostname: {0}, host: {1}".format(hostname, host))