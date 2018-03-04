import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# Super class for labels....
class SuperLabel():
	def __init__(self, logger, data_folder, x_offset, y_offset, date_format):
		self._logger = logger
		self._data_folder = data_folder
		self._date_format = date_format
		self._x_offset = x_offset * mm
		self._y_offset = y_offset * mm

		# 99012 is 36mm x 89.
		# Assume sub-class label the same unless it's overridden.
		self._width = 89 * mm
		self._height = 36 * mm

	# Returns filename of the created label
	def create_register_label(self, fob_id):
		try:
			# Setup the contents of the label.
			import socket
			hostname = socket.gethostname() + ".local"
			host = socket.gethostbyname(hostname)
			at_address1 = "at http://{0}".format(hostname)
			at_address2 = "or http://{0}".format(host)

			#####################################################
			# Use pdfgen to create our badge...
			#####################################################
			filename = self._data_folder + "/large-address-register.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			x_align = self._x_offset

			yPosition = 28 * mm + self._y_offset
			text = "Unknown Key Fob"
			c.setFont("Helvetica-Bold", 22)
			c.drawCentredString(self._width / 2, yPosition, text)

			# Please Register...
			yPosition = 20 * mm + self._y_offset
			text = "Please Register"
			c.setFont("Helvetica-Bold", 22)
			# So we can right align the dates to this.
			# Center Align
			c.drawCentredString(self._width / 2, yPosition, text)

			# At Address 1 http://...
			yPosition = 14 * mm + self._y_offset
			c.setFont("Helvetica", 12)
			c.drawString(x_align, yPosition, at_address1, mode=None)

			# Or Address 2 - http://...
			yPosition = 8 * mm + self._y_offset
			c.setFont("Helvetica", 12)
			c.drawString(x_align, yPosition, at_address2, mode=None)

			if not fob_id == "":
				yPosition = 3 * mm + self._y_offset
				c.setFont("Helvetica", 10)
				c.drawString(x_align, yPosition, "Key Fob: {0}".format(fob_id), mode=None)

			c.showPage()
			c.save()

			return filename
		except Exception as e:
			self._logger.error("Error creating register label. Error: {0}".format(e))
			return None

	# Create a generic text label (e.g. address label)
	def create_text_label(self, text):

		# TODO: text lines need to be split
		# into individual drawString lines
		# and moved down the label

		# from reportlab.lib.utils import simpleSplit
		# lines = simpleSplit(text, fontName, fontSize, maxWidth)

		try:
			# Setup the contents of the label.
			filename = self._data_folder + "/large-address-text.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			c.setFont("Helvetica", 14)
			commentWidth = c.stringWidth(text, "Helvetica", 14)
			if (commentWidth > (self._width * 0.9)):
				hScale = self._width * 0.9 / commentWidth
			else:
				hScale = 1

			c.scale(hScale, 1)
			c.drawString(4 * mm, 4 * mm, text, mode=None)

			c.showPage()
			c.save()

			return filename
		except Exception as e:
			self._logger.error("Error creating text label. Error: {0}".format(e))
			return None

	# Create a members name badge label
	def create_name_badge_label(self, name, comment):
		self._logger.info("Name badge label for : {0}".format(name))

		try:
			#####################################################
			# Use pdfgen to create our badge...
			#####################################################
			filename = self._data_folder + "/large-address-name-badge.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			# Configurable X-Offset to improve alignment
			x_align = self._x_offset


			## Taken from original Badger label (tagreader4.py)
			# Name...
			font_size = 60
			# So we can right align the dates to this.
			name_width = c.stringWidth(name, "Helvetica-Bold", font_size)
			# Shring the font size so it fits.
			if name_width > (self._width * 0.9):
				font_size = font_size  * self._width * 0.9 / name_width

			yPosition = 26 * mm + self._y_offset
			c.setFont("Helvetica-Bold", font_size )
			c.drawCentredString(self._width/2, 70-font_size/2,name)

			# Comment
			yPosition = 14 * mm + self._y_offset
			c.setFont("Helvetica", 14)
			c.translate(self._width / 2, 15)
			comment_width = c.stringWidth(comment, "Helvetica-Bold", 14)
			if (comment_width> (self._width * 0.9)):
				hScale = self._width * 0.9 / comment_width
			else:
				hScale = 1

			c.scale(hScale, 1)
			c.drawCentredString(0, 0, comment)

			c.showPage()
			c.save()

			return filename

		except Exception as e:
			self._logger.error("Error creating name badge label. Error: {0}".format(e))
			return None

	# Create a "HACK ME!" label
	def create_hack_me_label(self, label_serial_number, remove_after):

		try:
			#####################################################
			# Use pdfgen to create our badge...
			#####################################################
			filename = self._data_folder + "/large-address-hack-me.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			# Configurable X-Offset to improve alignment
			x_align = self._x_offset

			# Do Not Hack...
			yPosition = 18 * mm + self._y_offset
			text = "HACK ME!"
			c.setFont("Helvetica-Bold", 45)
			c.drawCentredString(self._width/2, yPosition, text)

			# Date Left
			date_now = datetime.date.today().strftime(self._date_format)
			date_left_message = "Date Left: {0}".format(date_now)
			yPosition =  2* mm + self._y_offset
			c.setFont("Helvetica", 12)
			c.drawString(x_align, yPosition, date_left_message, mode=None)

			# Item Details
			item_number = "#: {0}".format(label_serial_number)
			yPosition = 8 * mm + self._y_offset
			c.setFont("Helvetica", 12)
			c.drawString(x_align, yPosition, item_number, mode=None)

			c.showPage()
			c.save()

			return filename

		except Exception as e:
			self._logger.error("Error creating hack me label. Error: {0}".format(e))
			return None


	##~~ Helpers

	def get_right_align_x_position(self, canvas, text, font, font_size, align_to):
		if align_to > self._width:
			align_to = self._width - 10

		width = canvas.stringWidth(text, font, font_size)
		# Alight the text so it ends at the align to point
		# (hopefully the RHS of the main text)
		return align_to - width

	def get_contact_details(self, user_settings):
		email_address = user_settings.get("emailAddress")
		phone_number = user_settings.get("phoneNumber")
		twitter = user_settings.get("twitter")

		if not email_address == None and not email_address == "":
			return email_address
		elif not twitter == None and not twitter == "":
			return "@" + twitter
		elif not phone_number == None and not phone_number == "":
			return phone_number
		else:
			return "No contact details :-("
