from diff_drive import DifferentialDrive
from stepper_motor import StepperMotor
from PID import PID
from WiFiHandler import WifiHandler
from machine import ADC
from time import sleep_us, sleep
import gc


"""Tuning"""
pwm = 0.2
stepmode = "full"
Microsteps = None
Delay = 2000

# init motors and modes
motor1 = StepperMotor([0, 1, 2, 3], pwm_pct=pwm, frequency=25_000) # pins are ordered weird on this motor because the wires are twisted
motor2 = StepperMotor([4, 5, 6, 7], pwm_pct=pwm, frequency=25_000)
motor1.set_step_mode(stepmode, microsteps=Microsteps)
motor2.set_step_mode(stepmode, microsteps=Microsteps)
#init PID
pid = PID(kp = 7, ki = 0, kd = 0, target = 0, ldrmiddle=ADC(26), ldrright=ADC(28), ldrleft=ADC(27))
#init Controller object
controller = WifiHandler("NothingPhone(3)_9831", "PicoPassword", "10.149.229.128")
# init differential drive object
robot = DifferentialDrive(motor1, motor2, pid, controller,  wheelbase=238, wheel_dia=87, steps_per_rev=200, pid_period_us=1000, pid_scale=100000, min_delay=500)


robot._PIDorControllerinnit(stepmode, Microsteps)
try:
    while True:
        robot.runcontroller(pwm)
        sleep_us(Delay)
finally:
    robot._PID_Controller_stop()
    motor1.stop()
    motor2.stop()

