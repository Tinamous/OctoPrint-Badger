
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

	def print_do_not_hack_label(self, user, remove_after, label_serial_number):
		self._logger.warn("Null Label printer printing label...")
		filename = self._label.create_user_label(user, remove_after, label_serial_number)
		self._logger.warn("Do Not Hack label saved to: {0}".format(filename))

	def print_member_box_label(self, user):
		self._logger.info("Null Label printer printing members box label...")
		self._logger.info("User: {0}".format(user["name"]))
		filename = self._label.create_member_box_label(user)
		self._logger.warn("Members box label saved to: {0}".format(filename))

	def print_text_label(self, text):
		filename = self._label.create_text_label(text)
		self._logger.warn("Text label saved to: {0}".format(filename))

	def print_how_to_register(self, fob_id):
		self._logger.warn("Null Label printer printing how to register label...")
		filename = self._label.create_register_label(fob_id)
		self._logger.warn("Register label saved to: {0}".format(filename))

	def clear_print_queue(self):
		self._logger.warn("Null Label printer clear queue...")

	def get_print_queue(self):
		self._logger.warn("Null Label printer returning fake queue...")
		# TODO: Make it look like a real print queue
		print_queue = []
		print_queue.append(dict(jobId=1, description="Null Printer Job 1"))
		return print_queue

	def cancel_old_print_jobs(self):
		self._logger.warn("Null printer cancel old print jobs (Not implemente)...")
		# TODO: Cancel jobs older than x minutes...