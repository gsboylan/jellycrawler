''' 
Will allow control of a GPIO pin as well as the wiimote's rumble and leds using the A button and
the directional pad. 

Assumes that the raspberry pi's default bluetooth module is in discoverable mode.

In order to run set the pi temporarily to discoverable mode, run:
$ sudo hciconfig hci0 piscan

This program must be run as a superuser in order to take control of the raspberry pi's GPIO pins.
Unfortunately, the cwiid library is only compatible with Python 2, and will not run in Python 3.
'''

from __future__ import print_function
import cwiid
import RPi.GPIO as GPIO
import time

NUM_CONNECTION_TRIES = 5

raw_input('Press Enter to begin...')
print('Press 1 and 2 on your Wiimote now.')
wm = None
attempt = 0
while not wm:
	try:
		print('Attempt ', attempt + 1, ' of ', NUM_CONNECTION_TRIES)
		wm = cwiid.Wiimote()
	except RuntimeError:
		if (attempt < NUM_CONNECTION_TRIES):
			attempt += 1
		else:
			print('Maximum number of attempts reached. Exiting.')
			quit()
print('Connected to wiimote.')

wm.led = 15
wm.rumble = True
time.sleep(1)

wm.close()
