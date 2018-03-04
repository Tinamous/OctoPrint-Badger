import datetime

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from octoprint_Badger.Labels.SuperLabel import SuperLabel


# Defines the smaller label (89x36). Dymo: 99012
class LargeAddressLabelV2(SuperLabel):
	def __init__(self, logger, data_folder, x_offset, y_offset, date_format):
		SuperLabel.__init__(self, logger, data_folder, x_offset, y_offset, date_format)

		# Label Specifics.
		# set up page size parameters - 89 x 36 mm
		# this should be based on the label profile selected.
		self._width = 89 * mm
		# 99012 is 36mm
		self._height = 36 * mm
		# 11356 (Name Badge) is 42mm
		#self._height = 42 * mm


	# Creates a members Do Not Hack label
	# Returns filename of the created label
	def create_user_label(self, user, remove_after, label_serial_number):
		self._logger.info("User: {0}".format(user["name"]))
		username = user["name"];
		user_settings = user["settings"]

		displayName = user_settings.get("displayName")

		if displayName == None or displayName == "":
			displayName = username

		contact = self.get_contact_details(user_settings);

		try:
			#####################################################
			# Use pdfgen to create our badge...
			#####################################################
			filename = self._data_folder + "/large-address-donothack.pdf"
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

			# Date Left Date (LHS)
			yPosition = 19 * mm + self._y_offset
			date_now = datetime.date.today().strftime(self._date_format)
			c.setFont("Helvetica-Bold", 14)
			x_position = self.get_right_align_x_position(c, date_now, "Helvetica-Bold", 14, do_not_hack_width)
			c.drawString(x_align, yPosition, date_now, mode=None)

			# Remove After Date (RHS)
			yPosition = 19 * mm + self._y_offset
			date_remove_after = remove_after.strftime(self._date_format)
			c.setFont("Helvetica-Bold", 14)
			x_position = self.get_right_align_x_position(c, date_remove_after, "Helvetica-Bold", 14, do_not_hack_width)
			c.drawString(x_position, yPosition, date_remove_after, mode=None)

			# Member Details
			font_size = 12

			# Name
			yPosition = 12 * mm + self._y_offset
			c.setFont("Helvetica-Bold", font_size)
			c.drawString(x_align, yPosition, displayName, mode=None)

			# Contact
			yPosition = 7 * mm + self._y_offset
			c.setFont("Helvetica", font_size)
			c.drawString(x_align, yPosition, contact, mode=None)

			# Item Details (RHS of member)
			font_size = 8
			yPosition = 2 * mm + self._y_offset
			c.setFont("Helvetica", font_size)
			item_number = "Item #: {0}".format(label_serial_number)
			c.drawString(x_align, yPosition, item_number, mode=None)


			c.showPage()
			c.save()

			return filename
		except Exception as e:
			self._logger.error("Error creating user label. Error: {0}".format(e))
			return None

	# Create a label for Members storage boxes
	# Returns filename of the created label
	def create_member_box_label(self, user):
		self._logger.info("User: {0}".format(user["name"]))
		username = user["name"];
		user_settings = user["settings"]

		displayName = user_settings.get("displayName")

		if displayName == None or displayName == "":
			displayName = username

		contact = self.get_contact_details(user_settings);

		try:
			#####################################################
			# Use pdfgen to create our badge...
			#####################################################
			filename = self._data_folder + "/large-address-members-box.pdf"
			c = canvas.Canvas(filename, pagesize=(self._width, self._height))

			# Configurable X-Offset to improve alignment
			x_align = self._x_offset

			#############################################################
			# Copied from badger
			#############################################################

			# Now shrink font until name fits...
			fontSize = 60
			nameWidth = c.stringWidth(displayName, "Helvetica-Bold", 60)
			if (nameWidth > (self._width * 0.9)):
				fontSize = fontSize * self._width * 0.9 / nameWidth

			c.setFont("Helvetica-Bold", fontSize)
			c.drawCentredString(self._width / 2, 75 - fontSize / 2, displayName)

			#############################################################

			# TODO: Insert Barcode to allow for easy box check for
			# # members that have left

			# Do Not Hack...
			#yPosition = 26 * mm + self._y_offset
			#text = "DO NOT HACK"
			#c.setFont("Helvetica-Bold", 30)
			# So we can right align the dates to this.
			#do_not_hack_width = c.stringWidth(text, "Helvetica-Bold", 30)
			# Actual position for right aligntment
			#do_not_hack_width = do_not_hack_width + x_align
			#c.drawString(x_align, yPosition, text, mode=None)

			# Contact
			yPosition = 2 * mm + self._y_offset
			c.setFont("Helvetica", 14)
			c.drawString(x_align, yPosition, contact, mode=None)

			c.showPage()
			c.save()

			return filename
		except Exception as e:
			self._logger.error("Error creating user label. Error: {0}".format(e))
			return None
