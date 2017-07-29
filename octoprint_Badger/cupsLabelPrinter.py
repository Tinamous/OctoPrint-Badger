from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# Printing label using CUPS printing and canvas
# taken from MakeSpace Badger: https://github.com/Makespace/Badger
class cupsLabelPrinter():
	def __init__(self, logger, settings, data_folder):
		self._logger = logger
		self._settings = settings
		self._conn = None
		self._data_folder = data_folder

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

	def print_label(self):
		import cups
		self._logger.info("Cups Label printer printing label...")

	def print_how_to_register(self):
		self._logger.info("Cups Label printer printing how to register label...")

		import cups

		# set up page size parameters - 89 x 36 mm
		# this should be based on the label profile selected.
		self.w = 89 * mm
		self.h = 36 * mm

		name = "Please Register"
		comment = "at http://trovebadger.local or http://10.0.0.xx"

		try:
			#####################################################
			# Use pdfgen to create our badge...
			#####################################################
			c = canvas.Canvas(self._data_folder + "tagbadge.pdf", pagesize=(self.w, self.h))

			# Now shrink font until name fits...
			fontSize = 60
			nameWidth = c.stringWidth(name, "Helvetica-Bold", 60)
			if (nameWidth > (self.w * 0.9)):
				fontSize = fontSize * self.w * 0.9 / nameWidth

			c.setFont("Helvetica-Bold", fontSize)
			c.drawCentredString(self.w / 2, 70 - fontSize / 2, name)

			c.setFont("Helvetica", 14)

			c.translate(self.w / 2, 15)

			commentWidth = c.stringWidth(comment, "Helvetica-Bold", 14)
			if (commentWidth > (self.w * 0.9)):
				hScale = self.w * 0.9 / commentWidth
			else:
				hScale = 1

			c.scale(hScale, 1)
			c.drawCentredString(0, 0, comment)

			c.showPage()
			c.save()

			# ... and print it
			self._conn.printFile("DYMO-LabelWriter-450", self._data_folder + "tagbadge.pdf", "Badge", {})
		except Exception as e:
			self._logger.error("Error printing how to register tag. Error: {0}".format(e))