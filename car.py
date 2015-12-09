"""Defines basic utility functions for the car.
The goal of this module is to keep car variables separate from the main functionality for
cleanliness's sake, and to allow the main file to function regardless of the level of completion
achieved in the code here."""

from __future__ import print_function
import atexit
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_PWM_Servo_Driver

# Pointer to the _MOTORHAT for shutting off the motors on exit
_MOTORHAT = None

# Pre-translation car values. The motor and servo functions convert these into control signals.
BACKWARD = Adafruit_MotorHAT.BACKWARD
FORWARD = Adafruit_MotorHAT.FORWARD
RELEASE = Adafruit_MotorHAT.RELEASE
CURRENT_DIRECTION = RELEASE

# Range 0-100
CURRENT_SPEED = 0.0
# Motor speed resolution
_MAX_SPEED = 255
# Convert speed into int by parsing percentage of max speed
_MOTOR_SPEED = lambda: int((CURRENT_SPEED/100) * _MAX_SPEED)

# Range 0-100, center at 50
CURRENT_ROTATION = 50.0
# PWM ticks per cycle
_MAX_PWM_TICK = 4096
# Convert rotation into int tuple ranging from 0..4095 defining when to toggle _pwm signal
# Servo accepts 5-10% duty cycle
_SERVO_ROTATION = lambda: int(((CURRENT_ROTATION*0.035 + 5)/100.0) *  4095)

# PWM constants for controlling the servo. Channel is defined by where the servo is connected
# to the board, freq should generally be 1kHz.
PWM_FREQ = 50
PWM_CHANNEL = 15

# Pointers to the DC Motor objects
_DRIVE_MOTOR1 = None
_DRIVE_MOTOR2 = None

# Pointer to the _pwm controller
_pwm = None

def motor_setup():
	"""Get pointers to both of the motors and to the hat"""

	global _MOTORHAT
	_MOTORHAT = Adafruit_MotorHAT(addr=0x60)
	global _DRIVE_MOTOR1
	global _DRIVE_MOTOR2
	_DRIVE_MOTOR1 = _MOTORHAT.getMotor(1)
	_DRIVE_MOTOR2 = _MOTORHAT.getMotor(2)

def servo_setup():
	global _pwm
	_pwm = Adafruit_PWM_Servo_Driver.PWM(0x40)
	_pwm.setPWMFreq(PWM_FREQ)
	_pwm.setPWM(PWM_CHANNEL, 0, _SERVO_ROTATION())

def turnOffMotors():
	"""Set the motor speed to 0 and release both motors."""

	if _MOTORHAT:
		global CURRENT_DIRECTION
		global CURRENT_SPEED
		CURRENT_DIRECTION = RELEASE
		CURRENT_SPEED = 0.0

		_MOTORHAT.getMotor(1).setSpeed(_MOTOR_SPEED())
		_MOTORHAT.getMotor(2).setSpeed(_MOTOR_SPEED())
		_MOTORHAT.getMotor(1).run(CURRENT_DIRECTION)
		_MOTORHAT.getMotor(2).run(CURRENT_DIRECTION)

def turnOffPWM():
	"""set all PWM duty cycles to 0"""
	if _pwm:
		for channel in range (16):
			_pwm.setPWM(channel, 0, 0)

def set_direction(direction):
	"""Set the current direction of motor rotation.
	Direction should be FORWARD, BACKWARD, or RELEASE."""
	global CURRENT_DIRECTION
	CURRENT_DIRECTION = direction

def enable_motors():
	"""Applies whatever the current direction is to the motors to enable movement."""
	_DRIVE_MOTOR1.run(CURRENT_DIRECTION)
	_DRIVE_MOTOR2.run(CURRENT_DIRECTION)

def disable_motors():
	"""Releases the motors without changing the state variables."""
	_DRIVE_MOTOR1.run(RELEASE)
	_DRIVE_MOTOR2.run(RELEASE)

def increase_speed():
	"""Increase the speed by one percent and apply it to the motors.
	Only works when motors are active."""

	# Only do this if the motor is able to turn (direction agnostic)
	if CURRENT_DIRECTION:
		# First iterate the speed value
		global CURRENT_SPEED
		if (CURRENT_SPEED <= 95):
			CURRENT_SPEED += 5.0
		else:
			CURRENT_SPEED = 100

		_DRIVE_MOTOR1.setSpeed(_MOTOR_SPEED())
		_DRIVE_MOTOR2.setSpeed(_MOTOR_SPEED())

def decrease_speed():
	"""Decrease the speed by one percent and apply it to the motors.
	Only works when motors are active."""

	# Only do this if the motor is able to turn (direction agnostic)
	if CURRENT_DIRECTION:
		# First iterate the speed value
		global CURRENT_SPEED
		if (CURRENT_SPEED >= 5):
			CURRENT_SPEED -= 5.0
		else:
			CURRENT_SPEED = 0

		_DRIVE_MOTOR1.setSpeed(_MOTOR_SPEED())
		_DRIVE_MOTOR2.setSpeed(_MOTOR_SPEED())

def snap_speed(percent):
	# Only do this if the motor is able to turn (direction agnostic)
	if CURRENT_DIRECTION:
		if ((percent <= 100) and (percent >= 0)):
			global CURRENT_SPEED
			CURRENT_SPEED = percent

			_DRIVE_MOTOR1.setSpeed(_MOTOR_SPEED())
			_DRIVE_MOTOR2.setSpeed(_MOTOR_SPEED())

def rotate_right(percent):
	"""Decrease rotation by the percent specified, or 1 if not."""

	if not percent:
		percent = 1.0

	global CURRENT_ROTATION
	if (CURRENT_ROTATION >= percent):
		CURRENT_ROTATION -= percent

	_pwm.setPWM(PWM_CHANNEL, 0, _SERVO_ROTATION())

def rotate_left(percent):
	"""Increase rotation by the percent specified, or 1 if not."""

	if not percent:
		percent = 1.0

	global CURRENT_ROTATION
	if (CURRENT_ROTATION <= (100.0 - percent)):
		CURRENT_ROTATION += percent

	_pwm.setPWM(PWM_CHANNEL, 0, _SERVO_ROTATION())

def snap_rotate(percent):
	global CURRENT_ROTATION
	if (percent >= 0 and percent <= 100):
		CURRENT_ROTATION = float(percent)

	_pwm.setPWM(PWM_CHANNEL, 0, _SERVO_ROTATION())

atexit.register(turnOffMotors)
atexit.register(turnOffPWM)
