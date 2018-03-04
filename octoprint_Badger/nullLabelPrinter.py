import logging

# A dummy label printer just creates the label and leaves the pdf on disk
# for inspection/debugging.
class NullLabelPrinter():
	def __init__(self):
		# Temp one until assigned through initialize
		# which may not be called when getting the printers.
		self._logger = logging.getLogger('NullLabelPrinter')

	# Called before initialize as used by on_settings_load
	def get_printers(self):
		return ["Dymo_LabelWriter_NullType", "Another_Dymo_LabelWriter_NullType"]

	def initialize(self, logger, settings, data_folder, label):
		self._logger = logger
		self._settings = settings
		self._data_folder = data_folder
		self._label = label
		self._logger.info("Initialize null label printer")

	# 'printer-info': u'DYMO LabelWriter 450',
	# "printer-state"	"3" if the destination is idle, "4" if the destination is printing a job, and "5" if the destination is stopped.
	# 'printer-state-message': u'Rendering completed',
	# 'printer-state-reasons': [u'com.dymo.out-of-paper-error'],
	# 'printer-make-and-model': u'DYMO LabelWriter 450',
	def get_printer_info(self):

		return dict(
			info="Null Label Printer",
			state=3, # idle
			stateMessage="Rendering completed",
			# List.
			stateReasons=["com.dymo.out-of-paper-error"],
			makeAndModel="Null Printer V1",
		)

	def print_do_not_hack_label(self, user, remove_after, label_serial_number):
		self._logger.warn("Null Label printer printing label...")
		filename = self._label.create_user_label(user, remove_after, label_serial_number)
		self._logger.warn("Do Not Hack label saved to: {0}".format(filename))
		return 1

	def print_member_box_label(self, user):
		self._logger.info("Null Label printer printing members box label...")
		self._logger.info("User: {0}".format(user["name"]))
		filename = self._label.create_member_box_label(user)
		self._logger.warn("Members box label saved to: {0}".format(filename))
		return 2

	def print_text_label(self, text):
		filename = self._label.create_text_label(text)
		self._logger.warn("Text label saved to: {0}".format(filename))
		return 3

	def print_name_badge_label(self, name, comment):
		filename = self._label.create_name_badge_label(name, comment)
		self._logger.warn("Name badge label saved to: {0}".format(filename))
		return 5

	def print_hack_me_label(self, label_serial_number, remove_after):
		filename = self._label.create_hack_me_label(label_serial_number, remove_after)
		self._logger.warn("Hack me label saved to: {0}".format(filename))
		return 6

	def print_how_to_register(self, fob_id):
		self._logger.warn("Null Label printer printing how to register label...")
		filename = self._label.create_register_label(fob_id)
		self._logger.warn("Register label saved to: {0}".format(filename))
		return 4

	def clear_print_queue(self):
		self._logger.warn("Null Label printer clear queue...")

	def get_print_queue(self):
		self._logger.warn("Null Label printer returning fake queue...")
		# TODO: Make it look like a real print queue
		#print_queue = []
		#print_queue.append(dict(jobId=1, description="Null Printer Job 1"))
		return {48: {'job-uri': u'ipp://localhost:631/jobs/48'}, 49: {'job-uri': u'ipp://localhost:631/jobs/49'}, 47: {'job-uri': u'ipp://localhost:631/jobs/47'}}
		return print_queue

	def cancel_old_print_jobs(self):
		self._logger.warn("Null printer cancel old print jobs (Not implemente)...")
		# TODO: Cancel jobs older than x minutes...