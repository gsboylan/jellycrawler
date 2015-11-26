#!/usr/bin/python

from __future__ import print_function
import cwiid
import time
import car

# How many times connecting to the wiimote can fail before we kill the program
NUM_CONNECTION_TRIES = 5

# Pointer to the Wiimote object
WM = None

# Constants for handling inputs
_BUTTON_MODE = 0
_IRLEDS_MODE = 1
MODE = _BUTTON_MODE		# Default to button mode.

def wm_setup():
	raw_input('Press 1 and 2 on your Wiimote, then press Enter to begin.')
	attempt = 0
	global WM
	while not WM:
		try:
			print('Attempt ', attempt + 1, ' of ', NUM_CONNECTION_TRIES)
			WM = cwiid.Wiimote()
		except RuntimeError:
			if (attempt < NUM_CONNECTION_TRIES):
				attempt += 1
			else:
				print('Maximum number of attempts reached. Exiting.')
				quit()
	print('Connected to wiimote.')

	time.sleep(1)
	WM.rumble = True
	WM.led = cwiid.LED1_ON
	time.sleep(0.15)
	WM.led = cwiid.LED2_ON
	time.sleep(0.15)
	WM.led = cwiid.LED3_ON
	time.sleep(0.15)
	WM.led = cwiid.LED4_ON
	time.sleep(0.15)
	WM.led = 0
	WM.rumble = False

def mainloop_buttonMode():
	buttons = WM.state['buttons']
	# Buttons control movement and turning

	if (car._CURRENT_DIRECTION == car.FORWARD):
		# Up button increases speed, down button decreases speed.
		# Down (past 0) sets to backward.

		if (buttons & cwiid.BTN_UP):
			car.increase_speed()
		elif (buttons & cwiid.BTN_DOWN):
			car.decrease_speed()
			if (car._CURRENT_SPEED == 0):
				car.set_direction(car.BACKWARD)
	elif (car._CURRENT_DIRECTION == car.BACKWARD):
		# Up button decreases speed, down button increases speed.
		# Up (past 0) sets to foward.

		if (buttons & cwiid.BTN_UP):
			car.decrease_speed()
			if (car._CURRENT_SPEED == 0):
				car.set_direction(car.FORWARD)
		elif (buttons & cwiid.BTN_DOWN):
			car.increase_speed()
	else:
		# Set direction based on the button pressed,
		# This will only happen on startup or after turning off the motors, so
		# the speed will start off as 0

		if (buttons & cwiid.BTN_UP):
			car.set_direction(car.FORWARD)
		elif (buttons & cwiid.BTN_DOWN):
			car.set_direction(car.BACKWARD)

	# Only go if the button is being held
	if (buttons & cwiid.BTN_B):
		car.enable_motors()
	else:
		car.disable_motors()

	update_leds()

	# Only poll at ~60Hz to reduce strain on batteries
	time.sleep(0.0167)

def update_leds():
	"""Use the wiimote's LEDs as a speed indicator.
	Forward:
		0: 0%
		1: <25%
		12: 25-50%
		123: 50-75%
		1234: 75-100%
	Reverse:
		0: 0%
		4: <25%
		34: 25-50%
		234: 50-75%
		1234: 75-100%"""

	global WM
	if (car._CURRENT_DIRECTION == car.FORWARD):
		if (car._CURRENT_SPEED == 0):
			WM.led = 0
		elif (car._CURRENT_SPEED <= 25):
			WM.led = cwiid.LED1_ON
		elif (car._CURRENT_SPEED <= 50):
			WM.led = cwiid.LED1_ON | cwiid.LED2_ON
		elif (car._CURRENT_SPEED <= 75):
			WM.led = cwiid.LED1_ON | cwiid.LED2_ON | cwiid.LED3_ON
		else:
			WM.led = cwiid.LED1_ON | cwiid.LED2_ON | cwiid.LED3_ON | cwiid.LED4_ON
	elif (car._CURRENT_DIRECTION == car.BACKWARD):
		if (car._CURRENT_SPEED == 0):
			WM.led = 0
		elif (car._CURRENT_SPEED <= 25):
			WM.led = cwiid.LED4_ON
		elif (car._CURRENT_SPEED <= 50):
			WM.led = cwiid.LED4_ON | cwiid.LED3_ON
		elif (car._CURRENT_SPEED <= 75):
			WM.led = cwiid.LED4_ON | cwiid.LED3_ON | cwiid.LED2_ON
		else:
			WM.led = cwiid.LED4_ON | cwiid.LED3_ON | cwiid.LED2_ON | cwiid.LED1_ON
	else:
		WM.led = 0

if __name__ == "__main__":
	wm_setup()
	car.motor_setup()

	WM.rpt_mode = cwiid.RPT_BTN

	while True:
		mainloop_buttonMode()