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

def poll():
	if (MODE == _BUTTON_MODE):
		if (wm.state['buttons'] & cwiid.BTN_B):
			pass