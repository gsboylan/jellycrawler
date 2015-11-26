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

def callback_buttonMode(mesg_list, time):
	for mesg in mesg_list:
		if (mesg[0] == cwiid.MESG_BTN):
			# Buttons control movement and turning

			if (car._CURRENT_DIRECTION == car.FORWARD):
				# Up button increases speed, down button decreases speed.
				# Down (past 0) sets to backward.

				if (mesg[1] & cwiid.BTN_UP):
					car.increase_speed()
				elif (mesg[1] & cwiid.BTN_DOWN):
					car.decrease_speed()
					if (car._CURRENT_SPEED == 0):
						car.set_direction(car.BACKWARD)
			elif (car._CURRENT_DIRECTION == car.BACKWARD):
				# Up button decreases speed, down button increases speed.
				# Up (past 0) sets to foward.

				if (mesg[1] & cwiid.BTN_UP):
					car.decrease_speed()
					if (car._CURRENT_SPEED == 0):
						car.set_direction(car.FORWARD)
				elif (mesg[1] & cwiid.BTN_DOWN):
					car.increase_speed()
			else:
				# Set direction based on the button pressed, and start moving at the slowest speed
				# This will only happen on startup or after turning off the motors, so
				# the speed will start off as 0

				if (mesg[1] & cwiid.BTN_UP):
					car._CURRENT_DIRECTION = car.FORWARD
					car.increase_speed()
				elif (mesg[1] & cwiid.BTN_DOWN):
					car._CURRENT_DIRECTION = car.BACKWARD
					car.increase_speed()

			# Only go if the button is being held
			if (mesg[1] & cwiid.BTN_B):
				car.enable_motors()
			else:
				car.disable_motors()

if __name__ == "__main__":
	wm_setup()
	car.motor_setup()

	WM.rpt_mode = cwiid.RPT_BTN
	WM.mesg_callback = callback_buttonMode
	WM.enable(cwiid.FLAG_MESG_IFC)

	while True:
		pass