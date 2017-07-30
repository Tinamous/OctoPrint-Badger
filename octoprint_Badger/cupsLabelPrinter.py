
# Printing label using CUPS printing and canvas
# taken from MakeSpace Badger: https://github.com/Makespace/Badger
class CupsLabelPrinter():
	def __init__(self, logger, settings, data_folder, label):
		self._logger = logger
		self._settings = settings
		self._conn = None
		self._data_folder = data_folder
		self._label = label

	def initialize(self):
		self._logger.info("Initialize Cups Label Printer")
		# May fail on windows/test system without cups installed.
		try:
			self.initialize_printers()
		except Exception as e:
			self._logger.error("Failed to initialize error. Error: {0}".format(e))

	def initialize_printers(self):
		if not self._conn == None:
			# Already initialized
			return

		import cups
		self._conn = cups.Connection()

		# test to see if the label printer is installed
		self._printers = self._conn.getPrinters()

		for printer in self._printers:
			self._logger.info("Printers: {0}".format(printer))
			self._logger.info("Printers url: {0}".format(self._printers[printer]["device-uri"]))

		# TODO: See if the selected printer is available.
		try:
			selectedPrinter = self._settings.get(["printer"])
			self._printers[selectedPrinter]["device-uri"]
		except KeyError:
			self._logger.error("Selected printer not found")

	def get_printers(self):
		import cups
		self.initialize_printers()

		printers = []

		for printer in self._printers:
			printers.append(printer)
			self._logger.info("Printer: {0}".format(printer))
			self._logger.info("Printer... {0}".format(printers[printer]["device-uri"]))

		return printers

	# Print the Do Not Hack label
	def print_do_not_hack_label(self, user, remove_after, label_serial_number):
		self._logger.info("Cups Label printer printing DO NOT HACK label...")
		self._logger.info("User: {0}".format(user["name"]))
		filename = self._label.create_user_label(user, remove_after, label_serial_number)
		self.print_pdf(filename)

	def print_text_label(self, text):
		self._logger.info("Cups Label printer printing text label...")
		filename = self._label.create_text_label(text)
		self.print_pdf(filename)

	# Print the "How to register label" for users that are not registered
	# with the system.
	def print_how_to_register(self):
		self._logger.info("Cups Label printer printing how to register label...")
		filename = self._label.create_register_label()
		self.print_pdf(filename)

	def print_pdf(self, filename):
		try:
			# ... and print it
			import cups
			printer = self._settings.get(["printer"])
			self._logger.info("Printing '{0}' to printer: {1}".format(filename, printer))
			job_id = self._conn.printFile(printer, filename, "Badge", {})
			self._logger.info("Label was sent to the printer. Job id: {0}".format(job_id))

			if job_id == 0:
				self._logger.error("Label {0} did not print correctly.".format(filename))

		except Exception as e:
			self._logger.error("Error printing how to register tag. Error: {0}".format(e))