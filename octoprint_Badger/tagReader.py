import flask

from octoprint.util import RepeatedTimer

from .microRWDHiTag2Reader import MicroRWDHiTag2Reader
from .nullTagReader import NullTagReader

class TagReader():
	def __init__(self, logger, settings, event_bus):
		self._logger = logger
		self._settings = settings
		self._event_bus = event_bus
		self._rfidReader = NullTagReader(self._logger)
		self._check_tags_timer = None
		self._last_tag = None

	def on_shutdown(self):
		self._logger.info("Shutting down tag reader")
		if self._check_tags_timer:
			self._check_tags_timer = None

		if self._rfidReader:
			self._rfidReader.close()

	##~~ initialize_rfid_tag_reader
	def initialize(self):
		self._logger.info("Initializing Tag Reader")

		# Close the old reader (nullReader if not reader selected).
		if self._check_tags_timer:
			self._check_tags_timer = None

		if self._rfidReader:
			self._rfidReader.close()

		readerType = self._settings.get(['rfidReaderType'])
		if readerType == "Micro RWD HiTag2":
			self._logger.info("Initializing Micro RWD HiTag2")
			self._rfidReader = MicroRWDHiTag2Reader(self._logger)
		else:
			self._logger.info("Using null tag reader")
			self._rfidReader = NullTagReader(self._logger)

		if not self.try_initialze_tag_reader():
			self._logger.info("Failed to initialze RFID reader.")


	def try_initialze_tag_reader(self):
		try:
			rfidPort = self._settings.get(['rfidComPort'])
			if rfidPort:
				self._logger.info("Opening port: {0} for RFID reader.".format(rfidPort))
				self._rfidReader.open(rfidPort)
			else:
				self._logger.error("No COM port set for RFID reader")

			readerVersion = self._rfidReader.read_version()
			if readerVersion:
				self._logger.info("Reader reported version: {0}".format(readerVersion))
				# set the timer to check the reader for a tag
				self.startTimer()
				return True
			else:
				self._logger.error("Failed to read version from RFID Reader.")
				return False
		except IOError as e:
			self._logger.error("Failed to open the serial port.")
			return False


	def startTimer(self):
		self._logger.info("Starting timer to read RFID tag")
		self._check_tags_timer = RepeatedTimer(0.5, self.check_tag, None, None, True)
		self._check_tags_timer.start()

	def check_tag(self):
		try:
			tag = self._rfidReader.seekTag()

			# If it's the same tag as before, user has not released the tag
			# so just ignore it.
			if tag == self._last_tag:
				return

			if tag:
				self._logger.info("Got a tag!!!! TagId: {0}".format(tag))

				# Raise the tag seen event.
				payload = dict(tagId=tag)
				self._event_bus.fire("RfidTagSeen", payload)
				self._last_tag = tag
			else:
				# Clear last tag ready for a new one...
				self._last_tag = None
				self._logger.info("Tag removed")
		except IOError as e:
			self._logger.exception("Error reading tag. Exception: {0}".format(e))
		# TODO: Disable after too many errors
		except Exception as e:
			self._logger.exception("Unhandled error reading tag. Exception: {0}".format(e))

			# Find a way to indicate a fault.

