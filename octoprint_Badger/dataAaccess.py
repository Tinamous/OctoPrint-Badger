import sqlite3
import datetime

class DataAccess:
	def __init__(self, logger, settings, data_folder):
		self._logger = logger
		self._settings = settings
		self._data_folder = data_folder
		self._dbname = data_folder + "/badger.db"

		self._logger.info("Initialize Data Access")

		# Setup the database
		try:
			conn = sqlite3.connect(self._dbname)
			db = conn.cursor()

			self._logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
			self._logger.info("Create label counter")

			# Single entry database table used on startup to load the number of labels
			# printed on the current roll.
			db.execute('CREATE TABLE IF NOT EXISTS label_counter(id INTEGER PRIMARY KEY, labels_printed Number, labels_remaining Number, roll_number Number, replaced_at DateTime )')

			self._logger.info("Create serial number")

			# Single entry table to store the last number of the label.
			# uses ROWNUMBER from create label?!?!?
			db.execute('CREATE TABLE IF NOT EXISTS serial_number(id INTEGER PRIMARY KEY, serial INTEGER )')

			self._logger.info("Create item")

			# details of an item left
			# "Do Not Hack" or "Hack Me" item.
			db.execute('CREATE TABLE IF NOT EXISTS item(full_serial Text PRIMARY KEY, date_left DateTime, remove_after DateTime, user_name Text, comment Text, removed INTEGER, date_removed DateTime)')
		except Exception as e:
			self._logger.error("Failed to setup database. Error: {0}".format(e))


	def update_labels_used(self):
		sql = "SELECT id, labels_printed, labels_remaining FROM label_counter"
		rows = self.query(sql)

		if rows:
			# TODO: Ensure only a single row.
			row = rows[0]
			id = row[0]
			labels_printed = int(row[1])
			labels_remaining = int(row[2])

			labels_printed +=1
			labels_remaining -=1

			sql = "UPDATE label_counter SET labels_printed = " + str(labels_printed) + ", labels_remaining = " + str(labels_remaining) + "  WHERE id = " + str(id)
		else:
			sql = "INSERT INTO label_counter (labels_printed, labels_remaining, roll_number) VALUES ('%s', '%s', '%s')" % (1, 259, 1)

		self.execute(sql)


	def update_new_roll(self):
		sql = "SELECT id, roll_number FROM label_counter"
		rows = self.query(sql)

		if rows:
			# TODO: Ensure only a single row.
			row = rows[0]
			id = row[0]
			roll_number = int(row[1])
			roll_number +=1

			sql = "UPDATE label_counter SET roll_number = " + str(roll_number) + ", labels_remaining = " + str(260) + ",replaced_at = " + datetime.datetime.today() + "  WHERE id = " + str(id)
		else:
			sql = "INSERT INTO label_counter (labels_printed, labels_remaining, roll_number, replaced_at) VALUES ('%s','%s', '%s', '%s', '%s')" % (0, 260, 1, 250, datetime.datetime.today())

		self.execute(sql)


	def get_serial_number(self):
		serial = 13

		sql = "SELECT id,serial FROM serial_number"
		rows = self.query(sql)

		if rows:
			# TODO: Ensure only a single row.
			row = rows[0]
			id = row[0]
			serial = int(row[1])
			serial = serial + 1
			sql = "UPDATE serial_number SET serial = " + str(serial) + " WHERE id = " + str(id)

		else:
			sql = "INSERT INTO serial_number (serial) VALUES ('%s')" % (serial)


		self.execute(sql)
		return serial

	def store_item(self, serial,  user_name, remove_after):
		sql = "INSERT INTO item (full_serial, date_left, remove_after, user_name, comment, removed) VALUES ('%s', '%s', '%s', '%s', '', '0')" % (serial, datetime.datetime.today(), remove_after, user_name)
		self.execute(sql)

	def execute(self, sql):
		conn = sqlite3.connect(self._dbname)
		db = conn.cursor()

		db.execute(sql)
		conn.commit()
		conn.close()

	def query(self, sql):
		conn = sqlite3.connect(self._dbname)
		db = conn.cursor()

		db.execute(sql)
		try:
			return db.fetchall()
		finally:
			conn.close();

#  sql = "INSERT INTO connected (event_time, port, baudrate) VALUES ('%s', '%s', '%s')" % (datetime.datetime.today(), port, baudrate)

# sql = "SELECT hour, connected, disconnected, upload, print_started, print_done, print_failed, print_cancelled, print_paused, print_resumed, error FROM hourstat"
# rows = self.statDB.query(sql)
# hour.append(row[0])
