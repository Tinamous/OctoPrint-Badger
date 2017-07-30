from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

import datetime

# Defines the smaller label (89x36). Dymo: 99012
class LargeAddressLabel():
	def __init__(self, logger, data_folder, x_offset, y_offset, date_format):
		self._logger = logger
		self._data_folder = data_folder
		self._date_format = date_format

		# set up page size parameters - 89 x 36 mm
		# this should be based on the label profile selected.
		self._width = 89 * mm
		# 99012 is 36mm
		self._height = 36 * mm
		# 11356 (Name Badge) is 42mm
		#self._height = 42 * mm
		self._x_offset = x_offset * mm
		self._y_offset = y_offset * mm

	# Returns filename of the created label
	def create_user_label(self, user, remove_after, label_serial_number):
		self._logger.info("User: {0}".format(user["name"]))
		username = user["name"];
		user_settings = user["settings"]

		displayName = user_settings.get("displayName")

		if not displayName:
			displayName = username

		email_address = user_settings.get("emailAddress")
		phone_number = user_settings.get("phoneNumber")
		twitter = user_settings.get("twitter")

		contact = "No contact details"
		if not email_address == None:
			contact = email_address
		elif not twitter == None:
			contact = "@" + twitter
		elif not phone_number == None:
			contact = phone_number

		try:
			#####################################################
			# Use pdfgen to create our badge...
			#####################################################
			filename = self._data_folder + "\large-address-donothack.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			# Configurable X-Offset to improve alignment
			x_align = self._x_offset

			# Do Not Hack...
			yPosition = 26 * mm + self._y_offset
			text = "DO NOT HACK"
			c.setFont("Helvetica-Bold", 30)
			# So we can right align the dates to this.
			do_not_hack_width = c.stringWidth(text, "Helvetica-Bold", 30)
			# Actual position for right aligntment
			do_not_hack_width = do_not_hack_width + x_align
			c.drawString(x_align, yPosition, text, mode=None)

			# Date Left
			yPosition = 19 * mm + self._y_offset
			c.setFont("Helvetica", 12)
			c.drawString(x_align, yPosition, "Date Left:", mode=None)

			# Date Left Date (RHS)
			date_now = datetime.date.today().strftime(self._date_format)
			c.setFont("Helvetica-Bold", 12)
			x_position = self.get_right_align_x_position(c, date_now, "Helvetica-Bold", 12, do_not_hack_width)
			c.drawString(x_position, yPosition, date_now, mode=None)

			# Remove After
			yPosition = 14 * mm + self._y_offset
			c.setFont("Helvetica", 12)
			c.drawString(x_align, yPosition, "Remove After:", mode=None)

			# Remove After Date (RHS)
			date_remove_after = remove_after.strftime(self._date_format)
			c.setFont("Helvetica-Bold", 12)
			x_position = self.get_right_align_x_position(c, date_remove_after, "Helvetica-Bold", 12, do_not_hack_width)
			c.drawString(x_position, yPosition, date_remove_after, mode=None)

			# Member Details
			# Name
			yPosition = 8 * mm + self._y_offset
			c.setFont("Helvetica-Bold", 10)
			c.drawString(x_align, yPosition, displayName, mode=None)

			# Item Details (RHS of member)
			c.setFont("Helvetica", 10)
			item_number = "#: {0}".format(label_serial_number)
			x_position = self.get_right_align_x_position(c, item_number, "Helvetica", 10, do_not_hack_width)
			c.drawString(x_position, yPosition, item_number, mode=None)

			# Contact
			yPosition = 3 * mm + self._y_offset
			c.setFont("Helvetica", 10)
			c.drawString(x_align, yPosition, contact, mode=None)


			c.showPage()
			c.save()

			return filename
		except Exception as e:
			self._logger.error("Error creating user label. Error: {0}".format(e))
			return None

	def get_right_align_x_position(self, canvas, text, font, font_size, align_to):
		if align_to > self._width:
			align_to = self._width - 10

		width = canvas.stringWidth(text, font, font_size)
		# Alight the text so it ends at the align to point
		# (hopefully the RHS of the main text)
		return align_to - width


	def create_text_label(self, text):

		# TODO: text lines need to be split
		# into individual drawString lines
		# and moved down the label

		#from reportlab.lib.utils import simpleSplit
		#lines = simpleSplit(text, fontName, fontSize, maxWidth)

		try:
			# Setup the contents of the label.
			filename = self._data_folder + "\large-address-text.pdf"
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

	# Returns filename of the created label
	def create_register_label(self):
		try:
			# Setup the contents of the label.
			import socket
			hostname = socket.gethostname()
			host = socket.gethostbyname(hostname)
			comment = "at http://{0}.local or http://{1}".format(hostname, host)
			name = "Please Register"

			#####################################################
			# Use pdfgen to create our badge...
			#####################################################
			filename = self._data_folder + "\large-address-register.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			# Name
			# Now shrink font until name fits...
			fontSize = 36
			nameWidth = c.stringWidth(name, "Helvetica-Bold", 60)
			if (nameWidth > (self._width * 0.9)):
				fontSize = fontSize * self._width * 0.9 / nameWidth

			c.setFont("Helvetica-Bold", fontSize)
			#c.drawCentredString(self.w / 2, 70 - fontSize / 2, name)
			c.drawString(4 * mm, 4 * mm, name, mode=None)

			# The Comment.
			c.setFont("Helvetica", 14)
			c.translate(self._width / 2, 15)

			commentWidth = c.stringWidth(comment, "Helvetica-Bold", 14)
			if (commentWidth > (self._width * 0.9)):
				hScale = self._width * 0.9 / commentWidth
			else:
				hScale = 1

			c.scale(hScale, 1)
			c.drawString(4 * mm, 14 * mm, comment, mode=None)
			#c.drawCentredString(0, 0, comment)

			c.showPage()
			c.save()

			return filename
		except Exception as e:
			self._logger.error("Error creating register label. Error: {0}".format(e))
			return None