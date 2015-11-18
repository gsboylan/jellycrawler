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
WM = None
LED_ITER = 0
IS_SUPER = True
PWM_DUTY = 0
PWM = None

def main():
	raw_input('Press Enter to begin...')
	print('Press 1 and 2 on your Wiimote now.')
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
	time.sleep(0.5)
	WM.led = cwiid.LED2_ON
	time.sleep(0.5)
	WM.led = cwiid.LED3_ON
	time.sleep(0.5)
	WM.led = cwiid.LED4_ON
	time.sleep(0.5)
	WM.led = 0
	WM.rumble = False

	WM.rpt_mode = cwiid.RPT_BTN

	WM.mesg_callback = handle_callback
	WM.enable(cwiid.FLAG_MESG_IFC)

	GPIO.setmode(GPIO.BOARD)
	try:
		GPIO.setup(3, GPIO.OUT)
		global PWM
		PWM = GPIO.PWM(3, 100)
		PWM.start(60)
		print('Superuser detected, GPIO control enabled. Pin 3 is active PWM.')
	except RuntimeError:
		print('Not running as superuser, GPIO control is disabled.')
		global IS_SUPER
		IS_SUPER = False

	print('Press ctrl+c to disconnect and exit.')
	while True:
		pass

def handle_callback(msg_list, time):
	for msg in msg_list:
		if msg[0] == cwiid.MESG_BTN:
			WM.rumble = (msg[1] & cwiid.BTN_B)

			global LED_ITER
			if (msg[1] & cwiid.BTN_UP):
				LED_ITER += 1
			elif (msg[1] & cwiid.BTN_DOWN):
				LED_ITER -= 1
			WM.led = LED_ITER

			if IS_SUPER:
				global PWM_DUTY
				if (msg[1] & cwiid.BTN_RIGHT):
					if PWM_DUTY < 100:
						PWM_DUTY += 5
				elif (msg[1] & cwiid.BTN_LEFT):
					if PWM_DUTY > 0:
						PWM_DUTY -= 5

				# Toggle overrides PWM when active
				if (msg[1] & cwiid.BTN_A):
					PWM.ChangeDutyCycle(100)
				else:
					PWM.ChangeDutyCycle(PWM_DUTY)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
if WM:
	WM.close()
	try:
		GPIO.cleanup()
	except:
		pass