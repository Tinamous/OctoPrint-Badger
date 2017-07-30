from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

import datetime

# Defines the large label (100x54). Dymo: 99014
class ShippingLabel():
	def __init__(self, logger, data_folder, xOffset):
		self._logger = logger
		self._data_folder = data_folder
		self._date_format = "%Y-%m-%x"

		# Label size
		self._width = 101 * mm
		self._height = 54 * mm
		self._xOffset = xOffset * mm

	# Returns filename of the created label
	def create_user_label(self, user, remove_after):
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
			filename = self._data_folder + "\shipping-donothack.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			# Configurable X-Offset to improve alignment
			x_align = self._xOffset

			nameHeight = c.stringHeight("DO NOT HACK", "Helvetica-Bold", 30)
			self._logger.info("DO Not Hack Height: {0}".format(nameHeight))

			# Do Not Hack...
			c.setFont("Helvetica-Bold", 30)
			c.drawString(x_align, 18 * mm, "DO NOT HACK!", mode=None)

			# Date Left
			c.setFont("Helvetica", 12)
			c.drawString(x_align, 18 * mm, "Date Left:", mode=None)
			c.setFont("Helvetica-Bold", 12)
			date_now =  datetime.date.today().strftime(self._date_format)
			c.drawString(55 * mm, 18 * mm, date_now, mode=None)

			# Remove After
			c.setFont("Helvetica", 12)
			c.drawString(x_align, 13 * mm, "Remove After:", mode=None)

			date_remove_after = remove_after.strftime(self._date_format)
			c.setFont("Helvetica-Bold", 12)
			c.drawString(60 * mm, 13 * mm, date_remove_after, mode=None)

			# Member Details
			c.setFont("Helvetica-Bold", 10)
			c.drawString(x_align, 6 * mm, displayName, mode=None)
			c.setFont("Helvetica", 10)
			c.drawString(x_align, 1 * mm, contact, mode=None)

			# Item Details
			#item_number = "Item #: 37"
			#c.drawString(x_align, 1 * mm, item_number, mode=None)

			c.showPage()
			c.save()

			return filename
		except Exception as e:
			self._logger.error("Error creating user label. Error: {0}".format(e))
			return None

	def create_text_label(self, text):

		# TODO: text lines need to be split
		# into individual drawString lines
		# and moved down the label

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
			filename = self._data_folder + "\shipping-register.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			# Name
			# Now shrink font until name fits...
			fontSize = 36
			nameWidth = c.stringWidth(name, "Helvetica-Bold", 60)
			if (nameWidth > (self.width * 0.9)):
				fontSize = fontSize * self.width * 0.9 / nameWidth

			c.setFont("Helvetica-Bold", fontSize)
			#c.drawCentredString(self.w / 2, 70 - fontSize / 2, name)
			c.drawString(4 * mm, 4 * mm, name, mode=None)

			# The Comment.
			c.setFont("Helvetica", 14)
			c.translate(self.width / 2, 15)

			commentWidth = c.stringWidth(comment, "Helvetica-Bold", 14)
			if (commentWidth > (self.width * 0.9)):
				hScale = self.width * 0.9 / commentWidth
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
