from diff_drive import DifferentialDrive
from stepper_motor import StepperMotor
from time import sleep

"""Tuning"""
pwm = 0.75
stepmode = "half"
Microsteps = None
Delay = 0.001

# init motors and modes
motor1 = StepperMotor([0, 3, 1, 2], pwm_pct=pwm, frequency=18_000) # pins are ordered weird on this motor because the wires are twisted
motor2 = StepperMotor([4, 5, 6, 7], pwm_pct=pwm, frequency=18_000)
motor1.set_step_mode(stepmode, microsteps=Microsteps)
motor2.set_step_mode(stepmode, microsteps=Microsteps)

# init differential drive object
robot = DifferentialDrive(motor1, motor2, wheelbase=233, wheel_dia=87, steps_per_rev=200)

sleep(5) # wait 5 seconds to give us time to get the robot in place

# drive around a square meter
for i in range(4):
    robot.drive((1000), delay=Delay)
    sleep(0.5)
    robot.turn_in_place(90, delay=Delay)
    sleep(0.5)

robot.motor1.stop()
robot.motor2.stop()
