"""Defines basic utility functions for the car.
The goal of this module is to keep car variables separate from the main functionality for
cleanliness's sake, and to allow the main file to function regardless of the level of completion
achieved in the code here."""

from __future__ import print_function
import atexit
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

# Pre-translation car values. The motor and servo functions convert these into control signals.
_BACKWARD = 0
_FORWARD = 1
_RELEASE = -1
CURRENT_DIRECTION = _RELEASE

# Range 0-100
CURRENT_SPEED = 0.0
# Motor speed resolution
_MAX_SPEED = 255
# Convert speed into int by parsing percentage of max speed
MOTOR_SPEED = lambda: int((CURRENT_SPEED/100) * _MAX_SPEED)

# Range 0-100, center at 50
CURRENT_ROTATION = 50.0
# PWM ticks per cycle
_MAX_PWM_TICK = 4096
# Convert rotation into int tuple ranging from 0..4096 defining when to toggle pwm signal
SERVO_ROTATION = int((CURRENT_ROTATION/100)*4096)

# PWM constants for controlling the servo. Channel is defined by where the servo is connected
# to the board, freq should generally be 1kHz.
PWM_FREQ = 1000
PWM_CHANNEL = 0

# Pointers to the DC Motor objects
DRIVE_MOTOR1 = None
DRIVE_MOTOR2 = None

# Pointer to the pwm controller
pwm = None

def motor_setup():
	print('Setting up motors')

	motorhat = Adafruit_MotorHAT(addr=0x60)
	global DRIVE_MOTOR1
	global DRIVE_MOTOR2
	DRIVE_MOTOR1 = motorhat.getMotor(1)
	DRIVE_MOTOR2 = motorhat.getMotor(2)
	pass

def servo_setup():
	print('Setting up servos')
	
	global pwm
	# pwm = PWM(0x40)
	# pwm.setPWMFreq(PWM_FREQ)
	# pwm.setPWM(PWM_CHANNEL, 0, 0)

def turnOffMotors():
	"""Set the motor speed to 0 and release both motors."""

	print('Turning off motors')

	global CURRENT_DIRECTION
	global CURRENT_SPEED
	CURRENT_DIRECTION = _RELEASE
	CURRENT_SPEED = 0

	DRIVE_MOTOR1.setSpeed(MOTOR_SPEED())
	DRIVE_MOTOR2.setSpeed(MOTOR_SPEED())
	DRIVE_MOTOR1.run(Adafruit_MotorHAT.RELEASE)
	DRIVE_MOTOR2.run(Adafruit_MotorHAT.RELEASE)
	pass

def increase_speed():
	"""Increase the speed by one percent and apply it to the motors.
	Only works when motors are active."""

	# Only do this if the motor is able to turn (direction agnostic)
	if CURRENT_DIRECTION:
		# First iterate the speed value
		global CURRENT_SPEED
		if (CURRENT_SPEED < _MAX_SPEED):
			CURRENT_SPEED += 1

			DRIVE_MOTOR1.setSpeed(MOTOR_SPEED())
			DRIVE_MOTOR2.setSpeed(MOTOR_SPEED())

def decrease_speed():
	"""Decrease the speed by one percent and apply it to the motors.
	Only works when motors are active."""

	# Only do this if the motor is able to turn (direction agnostic)
	if CURRENT_DIRECTION:
		# First iterate the speed value
		global CURRENT_SPEED
		if (CURRENT_SPEED < _MAX_SPEED):
			CURRENT_SPEED -= 1

			DRIVE_MOTOR1.setSpeed(MOTOR_SPEED())
			DRIVE_MOTOR2.setSpeed(MOTOR_SPEED())

def snap_speed(percent):
	# Only do this if the motor is able to turn (direction agnostic)
	if CURRENT_DIRECTION:
		if ((percent <= 100) and (percent >= 0)):
			global CURRENT_SPEED
			CURRENT_SPEED = percent

			DRIVE_MOTOR1.setSpeed(MOTOR_SPEED())
			DRIVE_MOTOR2.setSpeed(MOTOR_SPEED())

def rotate_right(percent):
	"""Increase rotation by the percent specified, or 1 if not."""

	if not percent:
		percent = 1

	global CURRENT_ROTATION
	CURRENT_ROTATION += percent

	pwm.setPWM(PWM_CHANNEL, 0, SERVO_ROTATION())

