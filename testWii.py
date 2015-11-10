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
import sys
import pprint

NUM_CONNECTION_TRIES = 5

def handle_callback(msg_list, time):
	for msg in msg_list:
		pprint.pprint(msg)

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

wm.rumble = True
wm.led = cwiid.LED1_ON
time.sleep(0.1)
wm.led = cwiid.LED2_ON
time.sleep(0.1)
wm.led = cwiid.LED3_ON
time.sleep(0.1)
wm.led = cwiid.LED4_ON
time.sleep(0.1)
wm.led = 0
wm.rumble = False

wm.rpt_mode = cwiid.RPT_BTN

wm.mesg_callback = handle_callback
wm.enable(cwiid.FLAG_MESG_IFC)

print('Press ctrl+c to disconnect and exit.')
while True:
	pass

wm.close()

