
import logging
import logging.handlers

# Adapted from  https://github.com/Makespace/Badger/blob/master/tagreader4.py
class nullTagReader():
	def __init__(self, logger):
		self._logger = logger

	def open(self, port):
		self._logger.info("Null tag reader open port: {0}".format(port))

	def close(self):
		self._logger.info("Null tag reader closing serial port")

	def read_version(self):
		return 1

	def seekTag(self):
		return None