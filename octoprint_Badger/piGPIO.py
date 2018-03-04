# coding=utf-8
from __future__ import absolute_import

__author__ = "Stephen Harrison <Stephen.Harrison@AnalysisUK.com>"
__license__ = 'Creative Commons Share Alike 4.0'
__copyright__ = "Copyright (C) 2018 Analysis UK Ltd - Released under terms of the CC-SA-4.0 License"

from octoprint.util import RepeatedTimer

# Interface for real hardware on the raspberry Pi
class PiGPIO:
	def __init__(self, logger, settings, event_bus):
		self._logger = logger
		self._settings = settings
		self._event_bus = event_bus
		self._left_button_pin = 26
		self._left_led_pin = 16
		self._right_button_pin = 21
		self._right_led_pin = 20
		self._im_alive_pin = 11

		self._left_led_mode = 0
		self._right_led_mode = 0

		self._both_puttons_pressed = False
		self._leds_flash_on = False
		self._timer = RepeatedTimer(0.25, self.timer_tick, None, None, True)
		self._timer.start()

	def initialize(self):
		self._logger.info("Init RasPi GPIO...")

		# This will probably need to be extracted as it will
		# fail on PC when running in debug mode.
		import RPi.GPIO as GPIO

		# Left and right buttons
		GPIO.setup(self._left_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self._right_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		# Alive LED on Pi Power Hat.
		GPIO.setup(self._im_alive_pin, GPIO.OUT)

		# Left and right button LEDs
		GPIO.setup(self._left_led_pin, GPIO.OUT)
		GPIO.setup(self._right_led_pin, GPIO.OUT)

		# And turn on all the LEDs :-)
		self.set_alive_led(1)
		self.set_left_button_led(1)
		self.set_right_button_led(1)

	def set_alive_led(self, state):
		self._logger.info("Setting Alive LED")
		import RPi.GPIO as GPIO
		GPIO.output(self._im_alive_pin, state)

	def is_left_button_pressed(self):
		import RPi.GPIO as GPIO
		# Buttons are on pull-ups
		return not GPIO.input(self._left_button_pin)

	# State: 0 - off, 1 - on, 2 - blink
	def set_left_button_led(self, state):
		self._logger.info("Setting left button LED")
		self._left_led_mode = state
		self.set_led_state(self._left_led_pin, state)

	def is_right_button_pressed(self):
		import RPi.GPIO as GPIO
		# Buttons are on pull-ups
		return not GPIO.input(self._right_button_pin)

	# State: 0 - off, 1 - on, 2 - blink
	def set_right_button_led(self, state):
		self._logger.info("Setting right button LED")
		self._right_led_mode = state
		self.set_led_state(self._right_led_pin, state)

	def set_led_state(self, pin, state):
		import RPi.GPIO as GPIO
		if state == 0:
			GPIO.output(pin, False)
		else:
			GPIO.output(pin, True)

	def timer_tick(self):
		self._leds_flash_on = not self._leds_flash_on
		state = 0
		if self._leds_flash_on:
			state = 1

		if self._left_led_mode == 2:
			self._logger.info("Flashing Left LEDs....")
			self.set_led_state(self._left_led_pin, state)

		if self._right_led_mode == 2:
			self._logger.info("Flashing right LEDs....")
			self.set_led_state(self._right_led_pin, state)

		# Whilst we are on a timer tick..
		if self.is_left_button_pressed() & self.is_right_button_pressed():
			# Only fire the event once allowing for the buttons to
			# be released.
			if not self._both_puttons_pressed:
				self._both_puttons_pressed = True
				payload = dict()
				self._event_bus.fire("BothButtonsPressed", payload)
		else:
			self._both_puttons_pressed = False



