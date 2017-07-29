import serial
import logging
import logging.handlers

# Clever bits taken from https://github.com/Makespace/Badger/blob/master/tagreader4.py
# For RWD tag reader.
class microRWDHiTag2Reader():
	def __init__(self, logger):
		self._logger = logger
		self.serial_port = None

	def open(self, port):
		self._logger.info("Opening serial port '{0}' for tag reader".format(port))

		try:
			self.serial_port = serial.Serial(port, 9600, rtscts=1, timeout=0.2)
		except IOError as e:
			self._logger.error("Failed to open the serial port.")
		except OSError as e:
			self._logger.error("Failed to open the serial port. Has the port changed? Using: {0}".format(port))

	def close(self):
		try:
			self._logger.info("Closing serial port for tag reader")
			self.serial_port.close()
		except Exception as e:
			self._logger.exception("Failed to close the serial port. Exception: {0}".format(e))
			#Sink the exception as it's a close port operation.

	def read_version(self):
		# test the state of the tag reader,
		# return "None" if no tag present, or tag ID (in binary, four bytes)

		# We need to send the command soon after CTS becomes active (within 10mS)
		# so wait for that moment:
		while self.serial_port.getCTS():
			pass  # wait if CTS was already active

		# Put the quad reader into HITAG2 mode.
		self.serial_port.write(bytes([ 0x76, 0x01 ])) # v1
		self.serial_port.flush()
		response = self.serial_port.read()

		if response == "":
			self._logger.error ("Warning: Serial timeout getting RFID reader version. Is the reader connected?")
			return None

		value = ord(response)

		self._logger.info("Tag reader version response: " + response.encode('hex'))
		return value

	def tryTag(self):
		# test the state of the tag reader,
		# return "None" if no tag present, or tag ID (in binary, four bytes)

		# We need to send the command soon after CTS becomes active (within 10mS)
		# so wait for that moment:
		while self.serial_port.getCTS():
			pass  # wait if CTS was already active

		# Request the ID of the card from the reader.
		self.serial_port.write("U")
		self.serial_port.flush()

		# read response. Expect 5 bytes.
		# 1st byte is status code
		# then 4 bytes representing 0x01234567 style serial number for the card.
		response = self.serial_port.read()
		if response == "":
			self._logger.error("Warning: Serial timeout reading RFID tag")
			print "Warning: Serial timeout happened"
			return None
		if (ord(response) == 0xD6):  # tag present
			self._logger.info("0xD6 from reader: Tag present :-)")
			serial_number = self.serial_port.read(4)
			# Convert to hex for the application to use.
			self._logger.info("Tag reader read " + serial_number.encode('hex'))
			return serial_number.encode('hex')
		if (ord(response) == 0xC0):  # tag not present
			#self._logger.info("0xC0 from reader: Tag not present")
			return None
		print "Warning: Unexpected response from tag reader: " + response.encode('hex')
		return None

	# Tries to read a tag.
	# Returns the tag found.
	def seekTag(self):
		# Look for a genuine tag reading, and respond to it once for each touch
		# Debounces both arrival and departure of tag

		tag = self.tryTag()

		if tag == None:
			return None

		# Read it a second time to check
		# we have a valid tag.
		tag2 = self.tryTag()

		if tag2 == tag:
			self._logger.info("Tag seen: {0}".format(tag.encode('hex')))
			return tag
