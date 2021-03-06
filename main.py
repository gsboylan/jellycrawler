#!/usr/bin/python

from __future__ import print_function
import cwiid
import time
import sys
import car

# How many times connecting to the wiimote can fail before we kill the program
NUM_CONNECTION_TRIES = 5

# Pointer to the Wiimote object
WM = None

# Constants for handling inputs
_BUTTON_MODE = 0
_IRLEDS_MODE = 1
MODE = _BUTTON_MODE		# Default to button mode.

# Y difference defining when to stop moving
_CLOSEST_IR_DIFF = 450.0
_LAST_IR_DIFF = 0

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
	print('Initialized in manual control mode. Press 1 to switch to Infrared mode.')
	print('Press 2 while in Infrared mode to return to manual mode.')
	print('Press Home to quit.')

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

	if (buttons & cwiid.BTN_HOME):
		sys.exit(0)
	if (buttons & cwiid.BTN_1):
		global MODE
		MODE = _IRLEDS_MODE

	if (car.CURRENT_DIRECTION == car.FORWARD):
		# Up button increases speed, down button decreases speed.
		# Down (past 0) sets to backward.

		if (buttons & cwiid.BTN_UP):
			car.increase_speed()
		elif (buttons & cwiid.BTN_DOWN):
			car.decrease_speed()
			if (car.CURRENT_SPEED == 0):
				car.set_direction(car.BACKWARD)
	elif (car.CURRENT_DIRECTION == car.BACKWARD):
		# Up button decreases speed, down button increases speed.
		# Up (past 0) sets to foward.

		if (buttons & cwiid.BTN_UP):
			car.decrease_speed()
			if (car.CURRENT_SPEED == 0):
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

	if (buttons & cwiid.BTN_LEFT):
		car.rotate_right(None)
	elif (buttons & cwiid.BTN_RIGHT):
		car.rotate_left(None)

	# Only go if the button is being held
	if (buttons & cwiid.BTN_B):
		car.enable_motors()
	else:
		car.disable_motors()

	update_leds()

	# Only poll at ~60Hz to reduce strain on batteries
	time.sleep(0.0167)

def mainloop_irMode():
	buttons = WM.state['buttons']
	ir_response = WM.state['ir_src']
	global _LAST_IR_DIFF

	car.set_direction(car.FORWARD)

	if (buttons & cwiid.BTN_HOME):
		sys.exit(0)
	if (buttons & cwiid.BTN_2):
		global MODE
		MODE = _BUTTON_MODE

	# First filter out empty slots in the ir report
	ir_points = [entry['pos'] for entry in ir_response if entry is not None]

	if (len(ir_points) == 2):
		# Ideal case
		x = (ir_points[0][0] + ir_points[1][0])/2
		percent = 100.0*(x/float(cwiid.IR_X_MAX))
		car.snap_rotate(percent)

		yDiff = abs(ir_points[0][1] - ir_points[1][1])

		_LAST_IR_DIFF = yDiff
		car.snap_speed(get_speed(yDiff))
		car.enable_motors()

	elif (len(ir_points) == 1):
		# Manageable case, poor remote aim OR the robot is too close.
		# Decrease speed, keep adjusting wheel rotation. Proceed with caution.
		x = ir_points[0][0]
		percent = 100.0*(x/float(cwiid.IR_X_MAX))
		car.snap_rotate(percent)

		speed = get_speed(_LAST_IR_DIFF)/2
		car.snap_speed(speed)
		car.enable_motors()

	elif (len(ir_points) >= 2):
		# how did we end up with more than two?
		# Either there's another strong source (unlikely) or the car is sideways and we're picking
		# up both the front and back. In this case, just pick the two with the most different Y 
		# Alternately the user's aim is just really bad and they're aiming at the wrong thing.
		# Can't really plan around that.
		
		# Get the highest y value
		p1 = max(ir_points, key=lambda entry: entry[1])

		# Get the lowest y value (don't return the same point if all y values are the same)
		ir_points.remove(p1)
		p2 = min(ir_points, key=lambda entry: entry[1])

		x = (p1[0] + p2[0])/2
		percent = 100.0*(x/float(cwiid.IR_X_MAX))
		car.snap_rotate(percent)

		yDiff = abs(p1[1] - p2[1])

		_LAST_IR_DIFF = yDiff
		car.snap_speed(get_speed(yDiff))
		car.enable_motors()

	else:
		# We should stop doing anything until the user aims properly
		car.disable_motors()

	update_leds()

	time.sleep(0.0167)

def get_speed(yDiff):
	"""Use the separation of Y points to calculate motor speed. Return speed as a percentage."""

	if (yDiff >= _CLOSEST_IR_DIFF):
		# Don't move when too close
		return 0
	elif (yDiff >= _CLOSEST_IR_DIFF*0.75):
		# Minimum movement speed when close
		return 25
	elif (yDiff < _CLOSEST_IR_DIFF*0.75):
		# When far enough away, move as a function of distance
		return ((1 - yDiff/_CLOSEST_IR_DIFF)*100)

def update_leds():
	"""
	Use the wiimote's LEDs as a speed indicator when in button mode
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
		1234: 75-100%

	Use the leds as a direction indicator when in IR mode. 
	"""

	global WM
	if (MODE == _BUTTON_MODE):
		if (car.CURRENT_DIRECTION == car.FORWARD):
			if (car.CURRENT_SPEED == 0):
				WM.led = 0
			elif (car.CURRENT_SPEED <= 25):
				WM.led = cwiid.LED1_ON
			elif (car.CURRENT_SPEED <= 50):
				WM.led = cwiid.LED1_ON | cwiid.LED2_ON
			elif (car.CURRENT_SPEED <= 75):
				WM.led = cwiid.LED1_ON | cwiid.LED2_ON | cwiid.LED3_ON
			else:
				WM.led = cwiid.LED1_ON | cwiid.LED2_ON | cwiid.LED3_ON | cwiid.LED4_ON
		elif (car.CURRENT_DIRECTION == car.BACKWARD):
			if (car.CURRENT_SPEED == 0):
				WM.led = 0
			elif (car.CURRENT_SPEED <= 25):
				WM.led = cwiid.LED4_ON
			elif (car.CURRENT_SPEED <= 50):
				WM.led = cwiid.LED4_ON | cwiid.LED3_ON
			elif (car.CURRENT_SPEED <= 75):
				WM.led = cwiid.LED4_ON | cwiid.LED3_ON | cwiid.LED2_ON
			else:
				WM.led = cwiid.LED4_ON | cwiid.LED3_ON | cwiid.LED2_ON | cwiid.LED1_ON
		else:
			WM.led = 0
	elif (MODE == _IRLEDS_MODE):
		if (car.CURRENT_ROTATION <= 12.5):
			WM.led = cwiid.LED1_ON
		elif (car.CURRENT_ROTATION <= 25):
			WM.led = cwiid.LED1_ON | cwiid.LED2_ON
		elif (car.CURRENT_ROTATION <= 37.5):
			WM.led = cwiid.LED2_ON
		elif (car.CURRENT_ROTATION <= 62.5):
			WM.led = cwiid.LED2_ON | cwiid.LED3_ON
		elif (car.CURRENT_ROTATION <= 75):
			WM.led = cwiid.LED3_ON
		elif (car.CURRENT_ROTATION <= 87.5):
			WM.led = cwiid.LED3_ON | cwiid.LED4_ON
		else:
			WM.led = cwiid.LED4_ON

def main():
	wm_setup()
	car.motor_setup()
	car.servo_setup()

	WM.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_IR

	while True:
		if MODE == _IRLEDS_MODE:
			mainloop_irMode()
		else:
			mainloop_buttonMode()

if __name__ == "__main__":
	main()