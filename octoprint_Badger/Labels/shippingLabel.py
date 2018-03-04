import datetime

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from octoprint_Badger.Labels.SuperLabel import SuperLabel


# Defines the large label (100x54). Dymo: 99014
class ShippingLabel(SuperLabel):
	def __init__(self, logger, data_folder, x_offset, y_offset, date_format):
		SuperLabel.__init__(self, logger, data_folder, x_offset, y_offset, date_format)
		# Label size (for 99014 Label)
		self._width = 101 * mm
		self._height = 54 * mm

	# Creates a members Do Not Hack label
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
			filename = self._data_folder + "\shipping-donothack.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			# Configurable X-Offset to improve alignment
			x_align = self._x_offset

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
			#item_number = "Item #: {0}".format(label_serial_number)
			#c.drawString(x_align, 1 * mm, item_number, mode=None)

			c.showPage()
			c.save()

			return filename
		except Exception as e:
			self._logger.error("Error creating user label. Error: {0}".format(e))
			return None
