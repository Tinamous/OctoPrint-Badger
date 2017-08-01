import logging

# Printing label using CUPS printing and canvas
# taken from MakeSpace Badger: https://github.com/Makespace/Badger
class CupsLabelPrinter():

	# Used by on_settings_load before the class is initialized.
	def get_printers(self):
		import cups

		conn = cups.Connection()
		cups_printers = conn.getPrinters()

		printers = []

		for printer in cups_printers:
			printers.append(printer)

		return printers

	def initialize(self, logger, settings, data_folder, label):
		self._logger = logger
		self._settings = settings
		self._conn = None
		self._data_folder = data_folder
		self._label = label
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
		self._logger.info("Printers: {0}".format(self._printers))

		# TODO: See if the selected printer is available.
		try:
			selectedPrinter = self._settings.get(["printer"])
			uri = self._printers[selectedPrinter]["device-uri"]
			self._printer = self._printers[selectedPrinter]
		except KeyError:
			self._logger.error("Selected printer not found")

	# 'printer-info': u'DYMO LabelWriter 450',
	# "printer-state"	"3" if the destination is idle, "4" if the destination is printing a job, and "5" if the destination is stopped.
	# 'printer-state-message': u'Rendering completed',
	# 'printer-state-reasons': [u'com.dymo.out-of-paper-error'],
	def get_printer_info(self):
		if self._printer == None:
			return None
		else:
			return dict(
				info=self._printer["printer-info"],
				state=self._printer["printer-state"],
				stateMessage=self._printer["printer-state-message"],
				# List.
				stateReasons=self._printer["printer-state-reasons"],
				makeAndModel=self._printer["printer-make-and-model"],
			)

	# Print the Do Not Hack label
	def print_do_not_hack_label(self, user, remove_after, label_serial_number):
		self._logger.info("Cups Label printer printing DO NOT HACK label...")
		self._logger.info("User: {0}".format(user["name"]))
		filename = self._label.create_user_label(user, remove_after, label_serial_number)
		return self.print_pdf(filename)

	def print_member_box_label(self, user):
		self._logger.info("Cups Label printer printing members box label...")
		self._logger.info("User: {0}".format(user["name"]))
		filename = self._label.create_member_box_label(user)
		return self.print_pdf(filename)

	def print_text_label(self, text):
		self._logger.info("Cups Label printer printing text label...")
		filename = self._label.create_text_label(text)
		return self.print_pdf(filename)

	# Print the "How to register label" for users that are not registered
	# with the system.
	def print_how_to_register(self, fob_id):
		self._logger.info("Cups Label printer printing how to register label...")
		filename = self._label.create_register_label(fob_id)
		return self.print_pdf(filename)

	def print_pdf(self, filename):
		try:
			# ... and print it
			import cups
			printer = self._settings.get(["printer"])
			self._logger.info("Printing '{0}' to printer: {1}".format(filename, printer))
			# Doesn't appear to be getting cancelled automatically.
			job_id = self._conn.printFile(printer, filename, "Badge", {'job-cancel-after':'60'})
			self._logger.info("Label was sent to the printer. Job id: {0}".format(job_id))

			if job_id == 0:
				self._logger.error("Label {0} did not print correctly.".format(filename))

			return job_id

		except Exception as e:
			self._logger.error("Error printing label. Error: {0}".format(e))
			raise

	def clear_print_queue(self):
		self._logger.warn("Cups printer clear queue...")
		printer = self._settings.get(["printer"])
		self._conn.cancelAllJobs(printer)
		self._logger.warn("Cups printer queue cleared.")


	def get_print_queue(self):
		self._logger.warn("Cups printer returning jobs...")

		##attributes = self._conn.getJobAttributes(job, ["job-cancel-after", "job-hold-until",
		##                                               "job-printer-state-message", "job-printer-state-reasons"])

		jobs = self._conn.getJobs()
		self._logger.warn("Got jobs: {0}".format(jobs))
		for job in jobs:
			self._logger.info("Job:{0}".format(job))
			#self._logger.info("Job url: {0}".format(jobs[job]["job-uri"]))
		return jobs

	def cancel_old_print_jobs(self):
		self._logger.warn("Cups printer cancel old print jobs (Not implemente)...")
		# TODO: Cancel jobs older than x minutes...