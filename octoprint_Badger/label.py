from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

class largeAddressLabel():
	def __init__(self, logger, data_folder):
		self._logger = logger
		self._data_folder = data_folder

		# set up page size parameters - 89 x 36 mm
		# this should be based on the label profile selected.
		self.w = 89 * mm
		self.h = 36 * mm

	# Returns filename of the created label
	def create_user_label(self, user):
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
			c = canvas.Canvas(filename, pagesize=(self.w, self.h))

			x_align = 5 * mm

			# Do Not Hack...
			c.setFont("Helvetica-Bold", 30)
			c.drawString(x_align, 24 * mm, "DO NOT HACK!", mode=None)

			# Date Left
			c.setFont("Helvetica", 12)
			c.drawString(x_align, 18 * mm, "Date Left:", mode=None)
			c.setFont("Helvetica-Bold", 12)
			c.drawString(60 * mm, 18 * mm, "2017-07-29", mode=None)

			# Remove After
			c.setFont("Helvetica", 12)
			c.drawString(x_align, 13 * mm, "Remove After:", mode=None)
			c.setFont("Helvetica-Bold", 12)
			c.drawString(60 * mm, 13 * mm, "2017-07-29", mode=None)

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
			filename = self._data_folder + "\large-address-tagbadge.pdf"
			c = canvas.Canvas(filename, pagesize=(self.w, self.h))

			# Name
			# Now shrink font until name fits...
			fontSize = 36
			nameWidth = c.stringWidth(name, "Helvetica-Bold", 60)
			if (nameWidth > (self.w * 0.9)):
				fontSize = fontSize * self.w * 0.9 / nameWidth

			c.setFont("Helvetica-Bold", fontSize)
			#c.drawCentredString(self.w / 2, 70 - fontSize / 2, name)
			c.drawString(4 * mm, 4 * mm, name, mode=None)

			# The Comment.
			c.setFont("Helvetica", 14)
			c.translate(self.w / 2, 15)

			commentWidth = c.stringWidth(comment, "Helvetica-Bold", 14)
			if (commentWidth > (self.w * 0.9)):
				hScale = self.w * 0.9 / commentWidth
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


class shippingLabel():
	def __init__(self, logger, data_folder):
		self._logger = logger
		self._data_folder = data_folder

		# set up page size parameters - 89 x 36 mm
		# this should be based on the label profile selected.
		self.w = 101 * mm
		self.h = 54 * mm

	# Returns filename of the created label
	def create_user_label(self, user):
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
			c = canvas.Canvas(filename, pagesize=(self.w, self.h))

			x_align = 5 * mm

			# Do Not Hack...
			c.setFont("Helvetica-Bold", 30)
			c.drawString(x_align, 24 * mm, "DO NOT HACK!", mode=None)

			# Date Left
			c.setFont("Helvetica", 12)
			c.drawString(x_align, 18 * mm, "Date Left:", mode=None)
			c.setFont("Helvetica-Bold", 12)
			c.drawString(60 * mm, 18 * mm, "2017-07-29", mode=None)

			# Remove After
			c.setFont("Helvetica", 12)
			c.drawString(x_align, 13 * mm, "Remove After:", mode=None)
			c.setFont("Helvetica-Bold", 12)
			c.drawString(60 * mm, 13 * mm, "2017-07-29", mode=None)

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
			filename = self._data_folder + "\shipping-tagbadge.pdf"
			c = canvas.Canvas(filename, pagesize=(self.w, self.h))

			# Name
			# Now shrink font until name fits...
			fontSize = 36
			nameWidth = c.stringWidth(name, "Helvetica-Bold", 60)
			if (nameWidth > (self.w * 0.9)):
				fontSize = fontSize * self.w * 0.9 / nameWidth

			c.setFont("Helvetica-Bold", fontSize)
			#c.drawCentredString(self.w / 2, 70 - fontSize / 2, name)
			c.drawString(4 * mm, 4 * mm, name, mode=None)

			# The Comment.
			c.setFont("Helvetica", 14)
			c.translate(self.w / 2, 15)

			commentWidth = c.stringWidth(comment, "Helvetica-Bold", 14)
			if (commentWidth > (self.w * 0.9)):
				hScale = self.w * 0.9 / commentWidth
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