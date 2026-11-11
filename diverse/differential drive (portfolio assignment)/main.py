from diff_drive import DifferentialDrive
from stepper_motor import StepperMotor
from time import sleep
import gc

"""Tuning"""
pwm = 0.2
stepmode = "full"
Microsteps = None
Delay = 2000

# init motors and modes
motor1 = StepperMotor([0, 3, 1, 2], pwm_pct=pwm, frequency=25_000) # pins are ordered weird on this motor because the wires are twisted
motor2 = StepperMotor([4, 5, 6, 7], pwm_pct=pwm, frequency=25_000)
motor1.set_step_mode(stepmode, microsteps=Microsteps)
motor2.set_step_mode(stepmode, microsteps=Microsteps)

# init differential drive object
robot = DifferentialDrive(motor1, motor2, wheelbase=238, wheel_dia=87, steps_per_rev=200, delay_ramp=7000, pwm_ramp=0.15, total_accel_steps=100)


# robot.motor1.set_step([int(pwm * 0.25 * 65535), 0, 0, 0])
# robot.motor2.set_step([int(pwm * 0.25 * 65535), 0, 0, 0])
robot.drive(1700, Delay)



robot.motor1.stop()
robot.motor2.stop()


